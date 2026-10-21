from __future__ import annotations

import json
import re
import hashlib
import subprocess
import sys
import tarfile
import tempfile
import unittest
import shutil
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
            codex_manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
            self.assertEqual((manifest["name"], manifest["version"]), ("maurice", "0.1.0"))
            self.assertEqual({key: codex_manifest[key] for key in ("name", "version", "description", "author")}, {key: manifest[key] for key in ("name", "version", "description", "author")})
            self.assertEqual(codex_manifest["skills"], "./skills/")
            self.assertEqual(codex_manifest["interface"], manifest["extensions"]["com.openai"]["interface"])
            self.assertEqual(manifest["extensions"]["com.openai"]["interface"]["category"], "Productivity")
            self.assertEqual(manifest["extensions"]["com.openai"]["interface"]["displayName"], "Maurice")
            self.assertEqual(manifest["author"], {"name": "AgentMaurice"})
            self.assertLessEqual(len(manifest["extensions"]["com.openai"]["interface"]["shortDescription"]), 30)
            attestation = json.loads((plugin / "source-attestation.json").read_text())
            canonical_manifest = json.loads((CANONICAL / "skill-version.json").read_text())
            self.assertEqual(attestation["content_hash"], canonical_manifest["content_hash"])
            package_text = "\n".join(path.read_text(errors="ignore") for path in plugin.rglob("*") if path.is_file())
            self.assertNotIn("/Users/", package_text)
            self.assertNotIn("fixturesmachine", package_text)
            marketplace = json.loads((output / ".agents/plugins/marketplace.json").read_text())
            self.assertEqual(marketplace["name"], "maurice-local")
            self.assertEqual(marketplace["plugins"][0]["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL", "category": "Productivity"})
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

    def test_claude_package_and_archive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            result = self.run_builder(output, "claude")
            self.assertEqual(result.returncode, 0, result.stderr)
            plugin = output / "plugins" / "maurice"
            manifest = json.loads((plugin / "plugin.json").read_text())
            claude_manifest = json.loads((plugin / ".claude-plugin/plugin.json").read_text())
            self.assertEqual((manifest["name"], manifest["version"]), ("maurice", "0.1.0"))
            self.assertEqual({key: claude_manifest[key] for key in ("name", "version", "description", "author", "license")}, {key: manifest[key] for key in ("name", "version", "description", "author", "license")})
            self.assertEqual((plugin / "skills/maurice/SKILL.md").read_bytes(), (ROOT / "plugins/claude/maurice/SKILL.md").read_bytes())
            self.assertIn("maurice:", (plugin / "skills/maurice/SKILL.md").read_text())
            guides = ROOT / "plugins/claude/maurice"
            self.assertEqual(
                {path.relative_to(guides) for path in guides.rglob("*") if path.is_file()},
                {path.relative_to(plugin / "skills/maurice") for path in (plugin / "skills/maurice").rglob("*") if path.is_file()},
            )
            for source in guides.rglob("*.md"):
                target = plugin / "skills/maurice" / source.relative_to(guides)
                self.assertEqual(source.read_bytes(), target.read_bytes(), str(source))
                for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", target.read_text()):
                    if "://" not in link and not link.startswith("#"):
                        destination = (target.parent / link.split("#", 1)[0]).resolve()
                        self.assertTrue(destination.is_relative_to(plugin.resolve()), link)
                        self.assertTrue(destination.is_file(), f"broken packaged guide link: {link}")

            self.assertEqual((plugin / "README.md").read_bytes(), (ROOT / "plugins/claude/README.md").read_bytes())
            readme_text = (plugin / "README.md").read_text()
            self.assertIn("/maurice:maurice", readme_text)
            self.assertNotIn("/Users/", readme_text)
            self.assertNotIn("token", readme_text.lower())
            marketplace = json.loads((output / ".claude-plugin/marketplace.json").read_text())
            self.assertEqual(marketplace, {"name": "maurice-local", "owner": {"name": "AgentMaurice"}, "plugins": [{"name": "maurice", "source": "./plugins/maurice"}]})
            for source in CANONICAL.rglob("*"):
                if source.is_file():
                    target = plugin / "skills/agentmaurice" / source.relative_to(CANONICAL)
                    self.assertEqual(source.read_bytes(), target.read_bytes(), source.name)
            with tarfile.open(output / "maurice.plugin.tar.gz", "r:gz") as archive:
                names = archive.getnames()
            self.assertTrue(names)
            self.assertTrue(all(name == "maurice" or name.startswith("maurice/") for name in names))
            second = Path(tmp) / "out-second"
            self.assertEqual(self.run_builder(second, "claude").returncode, 0)
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(digest(output / "maurice.plugin.tar.gz"), digest(second / "maurice.plugin.tar.gz"))

    def test_corrupt_canonical_copy_and_template_symlink_are_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            copied = Path(tmp) / "repo"
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            canonical_file = copied / "skill/agentmaurice/SKILL.md"
            canonical_file.write_text(canonical_file.read_text() + "\ncorruption\n")
            output = Path(tmp) / "corrupt-out"
            result = subprocess.run([sys.executable, str(copied / "scripts/build_client_plugin.py"), "--client", "codex", "--output", str(output)], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())

            shutil.rmtree(copied)
            shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            template = copied / "plugins/codex/use-maurice/SKILL.md"
            template.unlink()
            template.symlink_to(canonical_file)
            result = subprocess.run([sys.executable, str(copied / "scripts/build_client_plugin.py"), "--client", "codex", "--output", str(Path(tmp) / "symlink-out")], text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)

    def test_claude_refuses_broken_and_escaping_guide_links(self) -> None:
        for link in ("references/missing.md", "../../../outside.md"):
            with self.subTest(link=link), tempfile.TemporaryDirectory() as tmp:
                copied = Path(tmp) / "repo"
                shutil.copytree(ROOT, copied, ignore=shutil.ignore_patterns(".git", "__pycache__"))
                guide = copied / "plugins/claude/maurice/SKILL.md"
                guide.write_text(guide.read_text() + f"\n[invalid]({link})\n")
                output = Path(tmp) / "out"
                result = subprocess.run(
                    [sys.executable, str(copied / "scripts/build_client_plugin.py"), "--client", "claude", "--output", str(output)],
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("lien de guide", result.stderr)
                self.assertFalse(output.exists())

    def test_refuses_invalid_outputs_and_client(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.assertNotEqual(self.run_builder(base / "out", "cursor").returncode, 0)
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
