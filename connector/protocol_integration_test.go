package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"sync/atomic"
	"testing"
	"time"
)

func fixtureMCP(t *testing.T, revoked *atomic.Bool) *httptest.Server {
	t.Helper()
	return httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("Authorization") != "Bearer test-secret" {
			http.Error(w, "invalid", 401)
			return
		}
		var q rpcRequest
		if err := json.NewDecoder(r.Body).Decode(&q); err != nil {
			t.Error(err)
			return
		}
		var result any
		switch q.Method {
		case "initialize":
			result = map[string]any{"protocolVersion": "2025-06-18", "capabilities": map[string]any{"tools": map[string]any{}}, "serverInfo": map[string]any{"name": "maurice", "version": "1"}}
		case "tools/list":
			tools := []any{}
			for _, name := range []string{"maurice.search", "maurice.explain", "maurice.execute"} {
				tools = append(tools, map[string]any{"name": name, "inputSchema": map[string]any{"type": "object"}})
			}
			result = map[string]any{"tools": tools}
		case "tools/call":
			if revoked.Load() {
				result = map[string]any{"isError": true, "content": []any{map[string]any{"type": "text", "text": "grant_invalid"}}, "structuredContent": map[string]any{"error": map[string]any{"code": "grant_invalid"}}}
			} else {
				result = map[string]any{"content": []any{}, "structuredContent": map[string]any{"results": []any{map[string]any{"ref": "workflow:fixture/proof@1"}}}}
			}
		default:
			t.Errorf("unexpected method %s", q.Method)
		}
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]any{"jsonrpc": "2.0", "id": q.ID, "result": result})
	}))
}

func TestRealEnvelopeAndHTTP200Revocation(t *testing.T) {
	var revoked atomic.Bool
	server := fixtureMCP(t, &revoked)
	defer server.Close()
	dir := privateTestDir(t)
	c := &connector{client: "codex", stateDir: dir, st: state{Version: stateVersion, Client: "codex", Origin: server.URL, Endpoint: server.URL + "/mcp", Token: "test-secret", ExpiresAt: time.Now().Add(time.Hour).Format(time.RFC3339)}}
	if err := c.saveLocked(); err != nil {
		t.Fatal(err)
	}
	if _, err := c.check(); err != nil {
		t.Fatal(err)
	}
	args := json.RawMessage(`{"name":"maurice.search","arguments":{}}`)
	value, err := c.call("tools/call", args)
	if err != nil {
		t.Fatal(err)
	}
	obj := value.(map[string]any)
	structured := obj["structuredContent"].(map[string]any)
	if _, ok := structured["results"]; !ok {
		t.Fatalf("remote CallToolResult was double wrapped: %#v", value)
	}
	fresh := &connector{client: "codex", stateDir: dir}
	if st, err := loadState(dir, "codex"); err == nil {
		fresh.st = st
	} else {
		t.Fatal(err)
	}
	if fresh.st.Verified {
		t.Fatal("new process trusted stored verification")
	}
	if _, err = fresh.toolsList(); err != nil {
		t.Fatal(err)
	}
	revoked.Store(true)
	value, err = fresh.call("tools/call", json.RawMessage(`{"name":"maurice.search","arguments":{}}`))
	if err != nil {
		t.Fatal(err)
	}
	encoded, _ := json.Marshal(value)
	if !bytes.Contains(encoded, []byte(`"code":"grant_invalid"`)) || !bytes.Contains(encoded, []byte(`"isError":true`)) {
		t.Fatalf("revocation lost: %s", encoded)
	}
	if bytes.Contains(encoded, []byte("test-secret")) {
		t.Fatal("credential leaked")
	}
	st, err := loadState(dir, "codex")
	if err != nil {
		t.Fatal(err)
	}
	if st.Token != "" || st.Verified {
		t.Fatal("revocation not persisted")
	}
}

func TestStreamReplyDoesNotWaitForServerToClose(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		var q rpcRequest
		_ = json.NewDecoder(r.Body).Decode(&q)
		w.Header().Set("Content-Type", "text/event-stream")
		_, _ = fmt.Fprintf(w, ": keepalive\n\ndata: {\"jsonrpc\":\"2.0\",\"id\":%s,\"result\":{}}\n\n", q.ID)
		w.(http.Flusher).Flush()
		<-r.Context().Done()
	}))
	defer server.Close()
	c := &connector{client: "codex", stateDir: privateTestDir(t), st: state{Version: stateVersion, Client: "codex", Origin: server.URL, Endpoint: server.URL + "/mcp", Token: "test-secret"}}
	started := time.Now()
	_, err := c.remoteRPC("tools/list", nil)
	if err != nil {
		t.Fatal(err)
	}
	if time.Since(started) > 2*time.Second {
		t.Fatal("waited for SSE EOF")
	}
}

func TestAtomicSaveDoesNotFollowPredictableTemporarySymlink(t *testing.T) {
	dir := privateTestDir(t)
	target := filepath.Join(t.TempDir(), "outside")
	if err := os.WriteFile(target, []byte("preserve"), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(target, filepath.Join(dir, "codex.json.tmp")); err != nil {
		t.Skip("symlinks not available")
	}
	c := &connector{client: "codex", stateDir: dir, st: state{Version: stateVersion, Client: "codex", Token: "test-secret"}}
	if err := c.saveLocked(); err != nil {
		t.Fatal(err)
	}
	got, _ := os.ReadFile(target)
	if string(got) != "preserve" {
		t.Fatal("predictable tmp symlink was followed")
	}
}

func TestMCPBodyBound(t *testing.T) {
	response := &http.Response{Header: http.Header{}, Body: io.NopCloser(bytes.NewReader(bytes.Repeat([]byte("x"), maxMessage+1)))}
	if _, err := readRPCBody(response); err == nil {
		t.Fatal("oversized body accepted")
	}
}
