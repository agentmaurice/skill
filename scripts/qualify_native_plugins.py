#!/usr/bin/env python3
"""Smoke-test the packaged Codex and Claude native MCP plugins.

The harness deliberately performs only local plugin installation and MCP
handshakes. It never starts a model turn and never calls a One endpoint.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import shlex
import shutil
import subprocess
import sys
import threading
import time
from typing import Any


EXPECTED_TOOLS = {
    "maurice.connection_status",
    "maurice.connect",
    "maurice.connection_check",
}


class QualificationError(RuntimeError):
    pass


def run_checked(argv: list[str], env: dict[str, str], cwd: Path) -> str:
    result = subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        detail = (result.stdout + "\n" + result.stderr).strip()[-4000:]
        raise QualificationError(
            f"command failed ({result.returncode}): {shlex.join(argv)}\n{detail}"
        )
    return result.stdout


class JsonRpcProcess:
    def __init__(self, argv: list[str], env: dict[str, str], cwd: Path):
        self.process = subprocess.Popen(
            argv,
            cwd=cwd,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )
        self.next_id = 0
        self._lines: queue.Queue[str | None] = queue.Queue()
        self._reader = threading.Thread(
            target=self._read_stdout,
            name="mcp-json-reader",
            daemon=True,
        )
        self._reader.start()

    def _read_stdout(self) -> None:
        stream = self.process.stdout
        if stream is None:
            self._lines.put(None)
            return
        try:
            while True:
                line = stream.readline()
                if not line:
                    break
                self._lines.put(line)
        finally:
            self._lines.put(None)

    def _write(self, payload: dict[str, Any]) -> None:
        if self.process.stdin is None:
            raise QualificationError("MCP stdin is unavailable")
        self.process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.process.stdin.flush()

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        self._write({"jsonrpc": "2.0", "method": method, "params": params or {}})

    def call(self, method: str, params: dict[str, Any] | None = None) -> Any:
        self.next_id += 1
        request_id = self.next_id
        self._write({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params or {}})
        if self.process.stdout is None:
            raise QualificationError("MCP stdout is unavailable")
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            wait = max(0.0, deadline - time.monotonic())
            try:
                line = self._lines.get(timeout=wait)
            except queue.Empty:
                break
            if line is None:
                break
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                continue
            if response.get("id") != request_id:
                continue
            if "error" in response:
                raise QualificationError(f"RPC {method} failed: {response['error']}")
            return response.get("result")
        code = self.process.poll()
        raise QualificationError(f"RPC {method} timed out or process exited ({code})")

    def close(self) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            self.process.wait(timeout=5)
        self._reader.join(timeout=1)
        if self.process.stdout is not None:
            self.process.stdout.close()


def structured_content(result: dict[str, Any]) -> dict[str, Any]:
    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured
    for content in result.get("content", []):
        if isinstance(content, dict) and content.get("type") == "text":
            try:
                value = json.loads(content.get("text", ""))
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                return value
    raise QualificationError("MCP tool response has no structured content")


def assert_tools(status: dict[str, Any], client: str) -> None:
    if status.get("runtimeStatus") != "connected":
        raise QualificationError(f"{client} MCP is not connected: {status}")
    tools = status.get("tools") or {}
    if set(tools) != EXPECTED_TOOLS:
        raise QualificationError(f"{client} exposed unexpected tools: {sorted(tools)}")


def native_environment(root: Path, key: str, profile: Path) -> dict[str, str]:
    profile.mkdir(parents=True, exist_ok=True)
    (root / "native-state").mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env[key] = str(profile)
    env["MAURICE_CONNECTOR_STATE_ROOT"] = str(root / "native-state")
    return env


def codex_smoke(codex: str, catalog: Path, scratch: Path) -> int:
    profile = scratch / "codex-profile"
    env = native_environment(scratch, "CODEX_HOME", profile)
    run_checked([codex, "plugin", "marketplace", "add", str(catalog)], env, scratch)
    run_checked([codex, "plugin", "add", "maurice@agentmaurice"], env, scratch)
    rpc = JsonRpcProcess([codex, "app-server", "--stdio"], env, scratch)
    try:
        rpc.call(
            "initialize",
            {
                "clientInfo": {"name": "native-client-smoke", "version": "1"},
                "capabilities": {"experimentalApi": True},
            },
        )
        rpc.notify("initialized")
        thread = rpc.call(
            "thread/start",
            {"cwd": str(scratch), "ephemeral": True, "sandbox": "read-only", "approvalPolicy": "never"},
        )
        thread_id = (thread or {}).get("thread", {}).get("id")
        if not thread_id:
            raise QualificationError("Codex thread/start returned no thread id")
        status = None
        for _ in range(30):
            response = rpc.call(
                "mcpServerStatus/list", {"threadId": thread_id, "detail": "full"}
            )
            status = next((item for item in response.get("data", []) if item.get("name") == "maurice"), None)
            if status and status.get("runtimeStatus") in {"connected", "failed"}:
                break
            time.sleep(0.5)
        if status is None:
            raise QualificationError("Codex MCP status did not list maurice")
        assert_tools(status, "Codex")
        result = rpc.call(
            "mcpServer/tool/call",
            {
                "server": "maurice",
                "threadId": thread_id,
                "tool": "maurice.connection_status",
                "arguments": {},
            },
        )
        state = structured_content(result)
        if state.get("client") != "codex" or state.get("status") != "disconnected":
            raise QualificationError(f"unexpected Codex connection status: {state}")
    finally:
        rpc.close()
    print("PASS codex.mcp.connected tools=3 connection_status=disconnected")
    return 1


def installed_claude_root(config: Path) -> Path:
    roots = sorted((config / "plugins" / "cache" / "agentmaurice" / "maurice").glob("*/.mcp.json"))
    if len(roots) != 1:
        raise QualificationError(f"expected one installed Claude plugin, found {len(roots)}")
    return roots[0].parent


def claude_smoke(claude: str, catalog: Path, scratch: Path) -> int:
    config = scratch / "claude-profile"
    env = native_environment(scratch, "CLAUDE_CONFIG_DIR", config)
    run_checked(
        [claude, "plugin", "install", "maurice", "--marketplace", str(catalog), "--scope", "user", "-y"],
        env,
        scratch,
    )
    health = run_checked([claude, "mcp", "list"], env, scratch)
    if "maurice" not in health.lower() or "connected" not in health.lower():
        raise QualificationError(f"Claude native MCP health did not report connected: {health[-2000:]}")

    root = installed_claude_root(config)
    manifest = json.loads((root / ".mcp.json").read_text(encoding="utf-8"))
    server = manifest.get("mcpServers", {}).get("maurice")
    if not isinstance(server, dict):
        raise QualificationError("installed Claude .mcp.json has no maurice server")
    command = server.get("command")
    if not isinstance(command, str):
        raise QualificationError("installed Claude MCP command is missing")
    command = command.replace("${CLAUDE_PLUGIN_ROOT}", str(root))
    if not os.path.isabs(command):
        command = str((root / command).resolve())
    argv = [command, *[str(arg) for arg in server.get("args", [])]]
    direct_env = env.copy()
    # Exercise the Claude-provided plugin data directory for this direct MCP
    # protocol check. The CLI health check above keeps its own native state.
    direct_env.pop("MAURICE_CONNECTOR_STATE_ROOT", None)
    direct_env["CLAUDE_PLUGIN_DATA"] = str(scratch / "claude-plugin-data")
    rpc = JsonRpcProcess(argv, direct_env, root)
    try:
        rpc.call(
            "initialize",
            {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "native-client-smoke", "version": "1"}},
        )
        rpc.notify("notifications/initialized")
        tools = rpc.call("tools/list")
        names = {item.get("name") for item in tools.get("tools", [])}
        if names != EXPECTED_TOOLS:
            raise QualificationError(f"Claude exposed unexpected tools: {sorted(names)}")
        result = rpc.call("tools/call", {"name": "maurice.connection_status", "arguments": {}})
        state = structured_content(result)
        if state.get("client") != "claude-code" or state.get("status") != "disconnected":
            raise QualificationError(f"unexpected Claude connection status: {state}")
    finally:
        rpc.close()
    print("PASS claude.mcp.health connected tools=3 connection_status=disconnected")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--scratch", required=True, type=Path)
    args = parser.parse_args()
    catalog = args.catalog.resolve()
    scratch = args.scratch.resolve()
    if not catalog.is_dir():
        raise QualificationError(f"catalog does not exist: {catalog}")
    scratch.mkdir(parents=True, exist_ok=True)
    if any(scratch.iterdir()):
        raise QualificationError(f"scratch must be empty: {scratch}")
    codex = shutil.which("codex")
    claude = shutil.which("claude")
    if not codex or not claude:
        raise QualificationError("codex and claude must both be available on PATH")
    passed = codex_smoke(codex, catalog, scratch)
    passed += claude_smoke(claude, catalog, scratch)
    print(f"SUMMARY pass={passed} fail=0 skip=0")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as error:
        print(f"QUALIFICATION_FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
