//go:build !windows

package main

import (
	"errors"
	"os"
	"path/filepath"
	"syscall"
	"time"
)

func acquireStateLock(dir string) (func(), error) {
	if err := checkStateParents(dir); err != nil {
		return nil, err
	}
	p := filepath.Join(dir, ".lock")
	f, err := os.OpenFile(p, os.O_CREATE|os.O_RDWR|syscall.O_NOFOLLOW, 0600)
	if err != nil {
		return nil, err
	}
	info, err := f.Stat()
	if err != nil {
		f.Close()
		return nil, err
	}
	if err = checkPrivate(p, info); err != nil {
		f.Close()
		return nil, err
	}
	deadline := time.Now().Add(30 * time.Second)
	for {
		err = syscall.Flock(int(f.Fd()), syscall.LOCK_EX|syscall.LOCK_NB)
		if err == nil {
			return func() { _ = syscall.Flock(int(f.Fd()), syscall.LOCK_UN); _ = f.Close() }, nil
		}
		if !errors.Is(err, syscall.EWOULDBLOCK) || time.Now().After(deadline) {
			f.Close()
			return nil, errors.New("state_locked")
		}
		time.Sleep(25 * time.Millisecond)
	}
}
