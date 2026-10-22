#!/usr/bin/env python3
"""Regression tests for the native plugin qualification harness."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "qualify_native_plugins.py"
SPEC = importlib.util.spec_from_file_location("qualify_native_plugins", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {SCRIPT}")
HARNESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = HARNESS
SPEC.loader.exec_module(HARNESS)


class JsonRpcProcessTests(unittest.TestCase):
    def test_reader_handles_batched_lines_before_pipe_eof(self) -> None:
        payload = "\n".join(
            [
                json.dumps({"jsonrpc": "2.0", "method": "notification"}),
                json.dumps({"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}),
                "",
            ]
        ).encode()
        child = (
            "import os,time; "
            f"os.write(1, {payload!r}); "
            "time.sleep(2)"
        )
        rpc = HARNESS.JsonRpcProcess(
            [sys.executable, "-c", child],
            {},
            Path.cwd(),
        )
        try:
            started = time.monotonic()
            result = rpc.call("test")
            elapsed = time.monotonic() - started
            self.assertEqual(result, {"ok": True})
            self.assertLess(elapsed, 1.0)
        finally:
            rpc.process.terminate()
            rpc.close()


class QualificationArgumentTests(unittest.TestCase):
    def test_github_source_requires_valid_ref_and_excludes_catalog(self) -> None:
        args = HARNESS.parse_arguments(
            ["--github-source", "owner/repo", "--ref", "plugins", "--scratch", "scratch"]
        )
        self.assertEqual(args.github_source, "owner/repo")
        self.assertEqual(args.ref, "plugins")
        rejected = [
            ["--github-source", "owner/repo", "--scratch", "scratch"],
            ["--catalog", "catalog", "--github-source", "owner/repo", "--ref", "plugins", "--scratch", "scratch"],
            ["--github-source", "owner/repo;echo", "--ref", "plugins", "--scratch", "scratch"],
        ]
        for argv in rejected:
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    HARNESS.parse_arguments(argv)

    def test_claude_health_requires_checkmark_connected(self) -> None:
        with self.assertRaises(HARNESS.QualificationError):
            HARNESS.assert_claude_health("plugin:maurice:maurice: ... Connected")
        HARNESS.assert_claude_health("plugin:maurice:maurice: ... \x1b[32m✔ Connected\x1b[0m")

    def test_native_data_root_is_profile_scoped_and_private(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "profile"
            env = HARNESS.native_environment("CODEX_HOME", profile)
            self.assertNotIn("MAURICE_CONNECTOR_STATE_ROOT", env)
            data_dir = profile / "plugins" / "data" / "owner-repo" / "connector" / "codex"
            data_dir.mkdir(parents=True)
            data_dir.chmod(0o700)
            self.assertEqual(HARNESS.assert_plugin_data_dir(profile, "codex"), data_dir)


if __name__ == "__main__":
    unittest.main()
