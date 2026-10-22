//go:build !windows

package main

import (
	"errors"
	"os"
	"syscall"
)

func makePrivate(path string, isDir bool) error {
	info, err := os.Lstat(path)
	if err != nil {
		return err
	}
	if info.Mode()&os.ModeSymlink != 0 {
		return errors.New("private_symlink_rejected")
	}
	mode := os.FileMode(0600)
	if isDir {
		mode = 0700
	}
	if err := os.Chmod(path, mode); err != nil {
		return err
	}
	return checkPrivate(path, infoAfterChmod(path))
}

func checkPrivate(path string, info os.FileInfo) error {
	if info == nil || info.Mode()&os.ModeSymlink != 0 {
		return errors.New("private_path_missing")
	}
	want := os.FileMode(0600)
	if info.IsDir() {
		want = 0700
	}
	if info.Mode().Perm() != want {
		return errors.New("private_mode_required")
	}
	st, ok := info.Sys().(*syscall.Stat_t)
	if !ok {
		return errors.New("private_owner_unavailable")
	}
	if uint32(st.Uid) != uint32(os.Getuid()) {
		return errors.New("private_owner_required")
	}
	return nil
}

func infoAfterChmod(path string) os.FileInfo { i, _ := os.Lstat(path); return i }
