package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"
)

func TestDisconnectForgetsCredentialsAcrossProcessesAndPermitsNewTarget(t *testing.T) {
	for _, pending := range []bool{true, false} {
		dir := privateTestDir(t)
		old := state{Version: stateVersion, Client: "codex", Origin: "https://old.example", Token: "synthetic-token", Endpoint: "https://old.example/mcp", Verified: true, SessionID: "synthetic-session"}
		if pending {
			old.Token = ""
			old.RequestID = strings.Repeat("A", 43)
			old.Verifier = "synthetic-verifier"
			old.PendingUntil = time.Now().Add(time.Minute).Format(time.RFC3339)
		}
		stale := &connector{client: "codex", stateDir: dir, st: old}
		if err := stale.saveLocked(); err != nil {
			t.Fatal(err)
		}
		fresh := &connector{client: "codex", stateDir: dir}
		result, err := fresh.disconnect()
		if err != nil {
			t.Fatal(err)
		}
		if result.(map[string]any)["authorization_may_remain_on_one"] != true {
			t.Fatal("forgot server authorization warning")
		}
		b, _ := os.ReadFile(statePath(dir, "codex"))
		if strings.Contains(string(b), "synthetic-") || strings.Contains(string(b), "old.example") {
			t.Fatal("private previous connection remained")
		}
		if _, err = stale.toolCall("maurice.search", json.RawMessage(`{}`)); err == nil || err.Error() != "not_connected" {
			t.Fatalf("stale credential: %v", err)
		}
		var srv *httptest.Server
		srv = httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			json.NewEncoder(w).Encode(map[string]any{"schema": "agentmaurice.assistant_pairing/v1", "request_id": strings.Repeat("B", 43), "user_code": "ABCD1234", "verification_uri": srv.URL + "/one/#/assistant-pairing/" + strings.Repeat("B", 43), "expires_at": time.Now().Add(time.Minute).Format(time.RFC3339), "interval_seconds": 1, "one_origin": srv.URL})
		}))
		if _, err = fresh.connect(srv.URL + "/one/#/"); err != nil {
			t.Fatalf("new explicit home target: %v", err)
		}
		srv.Close()
	}
}

func TestFreshRemoteCallDoesNotExposePrivateStatePath(t *testing.T) {
	c := &connector{client: "codex", stateDir: privateTestDir(t)}
	_, err := c.toolCall("maurice.search", json.RawMessage(`{}`))
	if err == nil || err.Error() != "not_connected" {
		t.Fatalf("fresh call leaked state error: %v", err)
	}
}
