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
if ($isDir) { $acl = New-Object -TypeName System.Security.AccessControl.DirectorySecurity } else { $acl = New-Object -TypeName System.Security.AccessControl.FileSecurity }
[void]$acl.SetAccessRuleProtection($true, $false)
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
[void]$acl.SetOwner($sid)
$flags = [System.Security.AccessControl.InheritanceFlags]::None
if ($isDir) { $flags = [System.Security.AccessControl.InheritanceFlags]'ContainerInherit,ObjectInherit' }
$rule = New-Object -TypeName System.Security.AccessControl.FileSystemAccessRule -ArgumentList @($sid, [System.Security.AccessControl.FileSystemRights]::FullControl, $flags, [System.Security.AccessControl.PropagationFlags]::None, [System.Security.AccessControl.AccessControlType]::Allow)
[void]$acl.AddAccessRule($rule)
Set-Acl -LiteralPath $p -AclObject $acl | Out-Null
Write-Output 'OK'`

const checkACLScript = `$ErrorActionPreference = 'Stop'
$p = $env:AM_PRIVATE_PATH
$acl = Get-Acl -LiteralPath $p
if (-not $acl.AreAccessRulesProtected) { throw 'inherited acl' }
$sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$owner = $acl.GetOwner([System.Security.Principal.SecurityIdentifier]).Value
if ($owner -ne $sid) { throw 'wrong owner' }
$allowed = @($sid, 'S-1-5-18', 'S-1-5-32-544')
$mine = $false
foreach ($r in $acl.GetAccessRules($true,$true,[System.Security.Principal.SecurityIdentifier])) {
  if ($r.AccessControlType -eq [System.Security.AccessControl.AccessControlType]::Allow) {
    if ($allowed -notcontains $r.IdentityReference.Value) { throw 'broad acl' }
    if ($r.IdentityReference.Value -eq $sid) { $mine = $true }
  }
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
