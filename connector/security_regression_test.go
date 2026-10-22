package main

import (
	"os"
	"path/filepath"
	"runtime"
	"strings"
	"testing"
)

// A persisted Verified bit is only a cache hint. A new process must not expose
// connected before it has re-proved the remote grant.
func TestStatusDoesNotTrustPersistedVerification(t *testing.T) {
	dir := privateTestDir(t)
	c := &connector{client: "codex", stateDir: dir, st: state{
		Version: stateVersion, Client: "codex", Origin: "https://one.example",
		Endpoint: "https://one.example/mcp", Token: "redacted", Verified: true,
	}}
	if err := c.saveLocked(); err != nil {
		t.Fatal(err)
	}
	fresh := &connector{client: "codex", stateDir: dir}
	if got := fresh.status()["status"]; got == "connected" {
		t.Fatalf("persisted verification produced false connected status: %#v", fresh.status())
	}
}

func TestLoadStateRejectsCredentialSymlink(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("symlink semantics require a Windows-specific privileged test")
	}
	dir := privateTestDir(t)
	target := filepath.Join(dir, "target.json")
	if err := os.WriteFile(target, []byte(`{"version":1,"client":"codex","token":"secret"}`), 0600); err != nil {
		t.Fatal(err)
	}
	if err := os.Symlink(target, filepath.Join(dir, "codex.json")); err != nil {
		t.Fatal(err)
	}
	if _, err := loadState(dir, "codex"); err == nil {
		t.Fatal("loadState followed a credential symlink")
	}
}

func TestResolveStateDirRejectsSymlinkedParent(t *testing.T) {
	if runtime.GOOS == "windows" {
		t.Skip("symlink semantics require a Windows-specific privileged test")
	}
	root := t.TempDir()
	realParent := filepath.Join(root, "real")
	if err := os.Mkdir(realParent, 0700); err != nil {
		t.Fatal(err)
	}
	linkParent := filepath.Join(root, "link")
	if err := os.Symlink(realParent, linkParent); err != nil {
		t.Fatal(err)
	}
	if _, err := resolveStateDir("codex", filepath.Join(linkParent, "state")); err == nil {
		t.Fatal("resolveStateDir accepted a symlinked parent")
	}
}

func TestSSEDataJoinsMultilineEventAndSkipsComments(t *testing.T) {
	got := string(sseData([]byte(": keepalive\ndata: {\"result\":\ndata: {\"ok\":true}}\n\n")))
	if !strings.Contains(got, `"ok":true`) || strings.Contains(got, "keepalive") {
		t.Fatalf("invalid multiline SSE payload: %q", got)
	}
}
