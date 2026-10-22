//go:build windows

package main

import (
	"crypto/sha256"
	"fmt"
	"runtime"
	"syscall"
	"unsafe"
)

func acquireStateLock(dir string) (func(), error) {
	// Win32 mutex ownership belongs to the OS thread, including across IO waits.
	runtime.LockOSThread()
	dll := syscall.NewLazyDLL("kernel32.dll")
	name, _ := syscall.UTF16PtrFromString(fmt.Sprintf("Local\\AgentMauriceConnector-%x", sha256.Sum256([]byte(dir))))
	h, _, err := dll.NewProc("CreateMutexW").Call(0, 0, uintptr(unsafe.Pointer(name)))
	if h == 0 {
		runtime.UnlockOSThread()
		return nil, err
	}
	result, _, waitErr := dll.NewProc("WaitForSingleObject").Call(h, 30000)
	if result != 0 && result != 0x80 {
		dll.NewProc("CloseHandle").Call(h)
		runtime.UnlockOSThread()
		return nil, fmt.Errorf("state_locked:%v", waitErr)
	}
	return func() {
		dll.NewProc("ReleaseMutex").Call(h)
		dll.NewProc("CloseHandle").Call(h)
		runtime.UnlockOSThread()
	}, nil
}
