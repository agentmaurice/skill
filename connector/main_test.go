package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
	"time"
)

func TestNormalizeOrigin(t *testing.T) {
	for _, tc := range []struct{ in, want string }{{"http://127.0.0.1:8080/one/", "http://127.0.0.1:8080"}, {"https://one.example/maurice", "https://one.example"}, {"https://One.Example", "https://one.example"}, {"http://[::1]/one", "http://[::1]"}} {
		got, err := normalizeOrigin(tc.in)
		if err != nil || got != tc.want {
			t.Fatalf("%q -> %q, %v", tc.in, got, err)
		}
	}
	for _, in := range []string{"http://example.com", "https://u:p@example.com", "https://example.com/?x=1", "https://example.com/other", "ftp://example.com"} {
		if _, err := normalizeOrigin(in); err == nil {
			t.Fatalf("accepted %q", in)
		}
	}
}

func TestNativePluginDataKeepsEachClientInItsHostProfile(t *testing.T) {
	root := privateTestDir(t)
	t.Setenv("MAURICE_CONNECTOR_STATE_ROOT", "")
	t.Setenv("PLUGIN_DATA", filepath.Join(root, "codex-profile"))
	t.Setenv("CLAUDE_PLUGIN_DATA", filepath.Join(root, "claude-profile"))
	for _, client := range []string{"codex", "claude-code"} {
		dir, err := resolveStateDir(client, "")
		profile := "codex-profile"
		if client == "claude-code" {
			profile = "claude-profile"
		}
		if err != nil || dir != filepath.Join(root, profile, "connector", client) {
			t.Fatalf("native %s state: %q, %v", client, dir, err)
		}
	}
}

func TestEndpointCannotCrossOrigin(t *testing.T) {
	if err := validateEndpoint("https://other.example/mcp", "https://one.example"); err == nil {
		t.Fatal("accepted remote endpoint from another origin")
	}
	if err := validateEndpoint("http://127.0.0.1:9001/mcp", "http://127.0.0.1:9000"); err != nil {
		t.Fatalf("rejected loopback relay: %v", err)
	}
	if err := validateEndpoint("http://example.com/mcp", "http://example.com"); err == nil {
		t.Fatal("accepted non-loopback HTTP endpoint")
	}
}

func TestPairingAndSinglePoll(t *testing.T) {
	dir := privateTestDir(t)
	_ = os.Chmod(dir, 0700)
	polls := 0
	var s *httptest.Server
	s = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/one/api/assistant-pairing/start" {
			w.Header().Set("Content-Type", "application/json")
			expires := time.Now().Add(5 * time.Minute).UTC().Format(time.RFC3339)
			_ = json.NewEncoder(w).Encode(map[string]any{"schema": "agentmaurice.assistant_pairing/v1", "request_id": strings.Repeat("A", 43), "user_code": "ABCD1234", "verification_uri": s.URL + "/one/#/assistant-pairing/" + strings.Repeat("A", 43) + "", "expires_at": expires, "interval_seconds": 1, "one_origin": s.URL})
			return
		}
		if r.URL.Path == "/one/api/assistant-pairing/poll" {
			polls++
			_ = json.NewEncoder(w).Encode(map[string]any{"status": "connected", "schema": "agentmaurice.assistant_pairing/v1", "token": "secret", "endpoint": s.URL + "/mcp/maurice", "grant_id": "g1", "expires_at": "2099-01-01T00:00:00Z"})
			return
		}
		if r.URL.Path == "/mcp/maurice" {
			var q rpcRequest
			_ = json.NewDecoder(r.Body).Decode(&q)
			w.Header().Set("Content-Type", "application/json")
			switch q.Method {
			case "initialize":
				_ = json.NewEncoder(w).Encode(map[string]any{"jsonrpc": "2.0", "id": q.ID, "result": map[string]any{"protocolVersion": "2025-06-18"}})
			case "tools/list":
				_ = json.NewEncoder(w).Encode(map[string]any{"jsonrpc": "2.0", "id": q.ID, "result": map[string]any{"tools": []any{map[string]any{"name": "maurice.search", "inputSchema": map[string]any{"type": "object"}}, map[string]any{"name": "maurice.explain", "inputSchema": map[string]any{"type": "object"}}, map[string]any{"name": "maurice.execute", "inputSchema": map[string]any{"type": "object"}}}}})
			case "tools/call":
				_ = json.NewEncoder(w).Encode(map[string]any{"jsonrpc": "2.0", "id": q.ID, "result": map[string]any{"content": []any{}, "structuredContent": map[string]any{"results": []any{}}}})
			}
			return
		}
		http.NotFound(w, r)
	}))
	defer s.Close()
	c := &connector{client: "codex", stateDir: dir, st: state{Version: stateVersion, Client: "codex"}}
	if _, err := c.connect(s.URL + "/one"); err != nil {
		t.Fatal(err)
	}
	if _, err := c.check(); err != nil {
		t.Fatal(err)
	}
	if polls != 1 {
		t.Fatalf("polls=%d", polls)
	}
	if _, err := c.check(); err != nil {
		t.Fatal(err)
	}
	b, err := os.ReadFile(filepath.Join(dir, "codex.json"))
	if err != nil {
		t.Fatal(err)
	}
	if string(b) == "" || string(b) == "\n" {
		t.Fatal("empty state")
	}
}

func TestNotificationAndToolCallEnvelope(t *testing.T) {
	c := &connector{client: "codex", st: state{Version: stateVersion, Client: "codex"}}
	v, err := c.call("tools/call", json.RawMessage(`{"name":"maurice.connection_status","arguments":{}}`))
	if err != nil {
		t.Fatal(err)
	}
	obj := v.(map[string]any)
	if _, ok := obj["content"]; !ok {
		t.Fatalf("missing content: %#v", obj)
	}
	if _, ok := obj["structuredContent"]; !ok {
		t.Fatalf("missing structuredContent: %#v", obj)
	}
}

func TestSSEData(t *testing.T) {
	b := sseData([]byte(": keepalive\ndata: {\"jsonrpc\":\"2.0\",\"id\":1,\"result\":{}}\n\n"))
	if string(b) != `{"jsonrpc":"2.0","id":1,"result":{}}` {
		t.Fatalf("SSE payload: %s", b)
	}
}

func TestStatePermissions(t *testing.T) {
	dir := privateTestDir(t)
	c := &connector{client: "codex", stateDir: dir, st: state{Version: stateVersion, Client: "codex", Token: "x"}}
	if err := c.saveLocked(); err != nil {
		t.Fatal(err)
	}
	info, err := os.Stat(filepath.Join(dir, "codex.json"))
	if err != nil || (runtime.GOOS != "windows" && info.Mode().Perm() != 0600) || checkPrivate(filepath.Join(dir, "codex.json"), info) != nil {
		t.Fatalf("state mode: %v %v", info.Mode(), err)
	}
}

func privateTestDir(t *testing.T) string {
	t.Helper()
	dir, err := resolveStateDir("codex", filepath.Join(t.TempDir(), "state"))
	if err != nil {
		t.Fatal(err)
	}
	return dir
}
