//go:build windows

package main

import (
	"errors"
	"os"
	"os/exec"
	"strings"
)

// Windows has no portable chmod equivalent. Use the OS ACL provider through
// PowerShell, with a constant script and the path supplied only via an env var.
// SYSTEM and local Administrators retain recovery access; inherited and broad
// user/group access is removed.
const privateACLScript = `$ErrorActionPreference = 'Stop'
$p = $env:AM_PRIVATE_PATH
if ([string]::IsNullOrWhiteSpace($p)) { throw 'missing path' }
$isDir = Test-Path -LiteralPath $p -PathType Container
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
$grant = if ($isDir) { "*$($sid.Value):(OI)(CI)F" } else { "*$($sid.Value):F" }
$system = if ($isDir) { '*S-1-5-18:(OI)(CI)F' } else { '*S-1-5-18:F' }
$admins = if ($isDir) { '*S-1-5-32-544:(OI)(CI)F' } else { '*S-1-5-32-544:F' }
& icacls.exe $p '/inheritance:r' '/grant:r' $grant $system $admins | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'icacls failed' }
& icacls.exe $p '/setowner' "*$($sid.Value)" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'icacls owner failed' }
Write-Output 'OK'`

const checkACLScript = `$ErrorActionPreference = 'Stop'
$p = $env:AM_PRIVATE_PATH
if ([string]::IsNullOrWhiteSpace($p)) { throw 'missing path' }
Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.Runtime.InteropServices;

public static class MauriceNativeSecurity {
  [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  private static extern uint GetNamedSecurityInfo(
    string objectName, uint objectType, uint securityInfo,
    out IntPtr owner, out IntPtr group, out IntPtr dacl, out IntPtr sacl,
    out IntPtr securityDescriptor);

  [DllImport("advapi32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
  private static extern bool ConvertSidToStringSid(IntPtr sid, out IntPtr stringSid);

  [DllImport("advapi32.dll", SetLastError = true)]
  private static extern bool GetSecurityDescriptorControl(IntPtr securityDescriptor, out ushort control, out uint revision);

  [DllImport("kernel32.dll")]
  private static extern IntPtr LocalFree(IntPtr handle);

  public static string GetOwner(string path) {
    IntPtr owner, group, dacl, sacl, descriptor;
    uint result = GetNamedSecurityInfo(path, 1, 1, out owner, out group, out dacl, out sacl, out descriptor);
    if (result != 0) throw new Win32Exception((int)result);
    try {
      IntPtr stringSid;
      if (!ConvertSidToStringSid(owner, out stringSid)) throw new Win32Exception(Marshal.GetLastWin32Error());
      try { return Marshal.PtrToStringUni(stringSid); }
      finally { LocalFree(stringSid); }
    } finally { LocalFree(descriptor); }
  }

  public static bool IsDaclProtected(string path) {
    IntPtr owner, group, dacl, sacl, descriptor;
    uint result = GetNamedSecurityInfo(path, 1, 4, out owner, out group, out dacl, out sacl, out descriptor);
    if (result != 0) throw new Win32Exception((int)result);
    try {
      ushort control;
      uint revision;
      if (!GetSecurityDescriptorControl(descriptor, out control, out revision)) throw new Win32Exception(Marshal.GetLastWin32Error());
      return (control & 0x1000) != 0;
    } finally { LocalFree(descriptor); }
  }
}
'@
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$owner = [MauriceNativeSecurity]::GetOwner($p)
if ($owner -ne $sid) { throw 'wrong owner' }
$protected = [MauriceNativeSecurity]::IsDaclProtected($p)
if (-not $protected) { throw 'inherited acl' }
$tmp = [System.IO.Path]::GetTempFileName()
Remove-Item -LiteralPath $tmp -Force
try {
  & icacls.exe $p '/verify' | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'icacls verify failed' }
  & icacls.exe $p '/save' $tmp | Out-Null
  if ($LASTEXITCODE -ne 0) { throw 'icacls save failed' }
  $sddl = @(Get-Content -LiteralPath $tmp | Where-Object { $_ -match '^D:' } | Select-Object -First 1)
  if ($sddl.Count -ne 1) { throw 'missing dacl' }
} finally {
  Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
}
$allowed = @($sid, 'SY', 'BA', 'S-1-5-18', 'S-1-5-32-544')
$mine = $false
foreach ($m in [regex]::Matches($sddl[0], '\(([^;]+);([^;]*);[^;]*;[^;]*;[^;]*;([^)]+)\)')) {
  if ($m.Groups[2].Value -match 'ID') { throw 'inherited acl' }
  if ($m.Groups[1].Value -ne 'A' -or $allowed -notcontains $m.Groups[3].Value) { throw 'broad acl' }
  if ($m.Groups[3].Value -eq $sid) { $mine = $true }
}
if (-not $mine) { throw 'owner access missing' }
Write-Output 'OK'`

func makePrivate(path string, _ bool) error {
	if _, err := os.Lstat(path); err != nil {
		return err
	}
	return runACL(privateACLScript, path)
}

func checkPrivate(path string, info os.FileInfo) error {
	if info.Mode()&os.ModeSymlink != 0 {
		return errors.New("unsafe_state_symlink")
	}
	if _, err := os.Lstat(path); err != nil {
		return err
	}
	return runACL(checkACLScript, path)
}

func runACL(script, path string) error {
	cmd := exec.Command("powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script)
	cmd.Env = append(os.Environ(), "AM_PRIVATE_PATH="+path)
	if out, err := cmd.Output(); err != nil || strings.TrimSpace(string(out)) != "OK" {
		return errors.New("private_acl_rejected")
	}
	return nil
}
