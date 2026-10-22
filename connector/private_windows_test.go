//go:build windows

package main

import (
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
)

func TestWindowsACLProviderOnItsOwnTemporaryDirectory(t *testing.T) {
	// Only this empty test directory is sent to PowerShell. Diagnostics cannot
	// contain a production credential path or a credential value.
	dir := filepath.Join(t.TempDir(), "acl-fixture")
	if err := os.Mkdir(dir, 0700); err != nil {
		t.Fatal(err)
	}
	for _, phase := range []struct{ name, script string }{{"restrict", privateACLScript}, {"verify", checkACLScript}} {
		cmd := exec.Command("powershell.exe", "-NoProfile", "-NonInteractive", "-Command", phase.script)
		cmd.Env = append(os.Environ(), "AM_PRIVATE_PATH="+dir)
		out, err := cmd.CombinedOutput()
		if err != nil || strings.TrimSpace(string(out)) != "OK" {
			t.Fatalf("ACL fixture phase %s: %v; PowerShell output: %s", phase.name, err, out)
		}
	}
}
