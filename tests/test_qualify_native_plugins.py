#!/usr/bin/env python3
"""Regression tests for the native plugin qualification harness."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
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


if __name__ == "__main__":
    unittest.main()
