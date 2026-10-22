//go:build windows

package main

import (
	"runtime"
	"testing"
	"time"
)

func TestWindowsStateLockSurvivesGoroutineScheduling(t *testing.T) {
	dir := privateTestDir(t)
	unlock, err := acquireStateLock(dir)
	if err != nil {
		t.Fatal(err)
	}
	acquired := make(chan error, 1)
	go func() {
		release, err := acquireStateLock(dir)
		if err == nil {
			release()
		}
		acquired <- err
	}()
	for i := 0; i < 50; i++ {
		runtime.Gosched()
		time.Sleep(time.Millisecond)
	}
	select {
	case err := <-acquired:
		unlock()
		t.Fatalf("concurrent process state access was not excluded: %v", err)
	default:
	}
	unlock()
	select {
	case err := <-acquired:
		if err != nil {
			t.Fatal(err)
		}
	case <-time.After(2 * time.Second):
		t.Fatal("Win32 mutex did not release after goroutine scheduling")
	}
}
