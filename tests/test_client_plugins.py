from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_client_plugin.py"
CANONICAL = ROOT / "skill" / "agentmaurice"


class ClientPluginBuild(unittest.TestCase):
    def run_builder(self, output: Path, client: str = "codex") -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(BUILDER), "--client", client, "--output", str(output)], cwd=ROOT, text=True, capture_output=True)

    def test_codex_package_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            result = self.run_builder(output)
            self.assertEqual(result.returncode, 0, result.stderr)
            plugin = output / "plugins" / "maurice"
            manifest = json.loads((plugin / "plugin.json").read_text())
            self.assertEqual((manifest["name"], manifest["version"]), ("maurice", "0.1.0"))
            self.assertEqual(manifest["extensions"]["com.openai"]["interface"]["category"], "Productivity")
            self.assertLessEqual(len(manifest["extensions"]["com.openai"]["interface"]["shortDescription"]), 30)
            attestation = json.loads((plugin / "source-attestation.json").read_text())
            canonical_manifest = json.loads((CANONICAL / "skill-version.json").read_text())
            self.assertEqual(attestation["content_hash"], canonical_manifest["content_hash"])
            package_text = "\n".join(path.read_text(errors="ignore") for path in plugin.rglob("*") if path.is_file())
            self.assertNotIn("/Users/", package_text)
            self.assertNotIn("fixturesmachine", package_text)
            marketplace = json.loads((output / ".agents/plugins/marketplace.json").read_text())
            self.assertEqual(marketplace["name"], "maurice-local")
            for source in CANONICAL.rglob("*"):
                if source.is_file():
                    target = plugin / "skills/agentmaurice" / source.relative_to(CANONICAL)
                    self.assertEqual(source.read_bytes(), target.read_bytes(), source.name)
            with tarfile.open(output / "maurice.plugin.tar.gz", "r:gz") as archive:
                names = archive.getnames()
            self.assertTrue(names)
            self.assertTrue(all(name == "maurice" or name.startswith("maurice/") for name in names))
            second = Path(tmp) / "out-second"
            self.assertEqual(self.run_builder(second).returncode, 0)
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest(output / "maurice.plugin.tar.gz"), digest(second / "maurice.plugin.tar.gz"))

    def test_refuses_invalid_outputs_and_client(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertNotEqual(self.run_builder(base / "out", "claude").returncode, 0)
            existing = base / "existing"
            existing.mkdir()
            (existing / "extra").write_text("x")
            self.assertNotEqual(self.run_builder(existing).returncode, 0)
            self.assertNotEqual(self.run_builder(ROOT).returncode, 0)
            link = base / "link"
            link.symlink_to(base, target_is_directory=True)
            result = self.run_builder(link)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("lien symbolique", result.stderr)


if __name__ == "__main__":
    unittest.main()
