#!/usr/bin/env python3
"""Build a self-contained Agent Plugins 1.0 package for a supported client."""

from __future__ import annotations

import argparse
import gzip
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "skill" / "agentmaurice"
PLUGIN_NAME = "maurice"
PLUGIN_VERSION = "0.1.0"
PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PLUGIN_DESCRIPTION = "Accéder aux Workflows AgentMaurice avec un mandat explicite."


def fail(message: str) -> "NoReturn":
    raise SystemExit(f"build_client_plugin: {message}")


def ensure_no_symlinks(root: Path) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            fail(f"symlink refusé: {path.relative_to(root)}")


def validate_canonical() -> dict:
    if not CANONICAL.is_dir() or CANONICAL.is_symlink():
        fail("skill canonique introuvable")
    ensure_no_symlinks(CANONICAL)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_v2_skill.py")], cwd=ROOT, check=True)
    return json.loads((CANONICAL / "skill-version.json").read_text(encoding="utf-8"))


def assert_output(output: Path) -> None:
    resolved = output.resolve()
    source = ROOT.resolve()
    if resolved == source or source in resolved.parents or resolved in source.parents:
        fail("--output doit être hors du checkout source")
    if output.exists() and output.is_symlink():
        fail("--output ne doit pas être un lien symbolique")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        fail("--output doit être un répertoire absent ou vide")


def copy_tree(src: Path, dst: Path) -> None:
    for path in sorted(src.rglob("*")):
        relative = path.relative_to(src)
        target = dst / relative
        if path.is_symlink():
            fail(f"symlink refusé: {relative}")
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build(output: Path, client: str) -> Path:
    if client != "codex":
        fail("seul --client codex est implémenté par AGENT-613")
    manifest = validate_canonical()
    assert_output(output)
    template = ROOT / "plugins" / "codex" / "use-maurice" / "SKILL.md"
    ensure_no_symlinks(ROOT / "plugins" / "codex")
    if not template.is_file():
        fail("template use-maurice introuvable")
    with tempfile.TemporaryDirectory(prefix="agentmaurice-plugin-") as temp:
        staging = Path(temp) / "output"
        plugin = staging / "plugins" / PLUGIN_NAME
        copy_tree(CANONICAL, plugin / "skills" / "agentmaurice")
        use_skill = plugin / "skills" / "use-maurice" / "SKILL.md"
        use_skill.parent.mkdir(parents=True, exist_ok=True)
        use_skill.write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        portable_manifest = {
            "$schema": PLUGIN_SCHEMA,
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {"name": "AgentMaurice"},
            "license": "Proprietary",
            "keywords": ["agentmaurice", "workflow", "mcp"],
            "extensions": {"com.openai": {"interface": {"displayName": "Maurice", "developerName": "AgentMaurice", "shortDescription": "Workflows AgentMaurice", "category": "Productivity"}}},
        }
        write_json(plugin / "plugin.json", portable_manifest)
        write_json(plugin / ".codex-plugin" / "plugin.json", {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {"name": "AgentMaurice"},
            "skills": "./skills/",
            "interface": portable_manifest["extensions"]["com.openai"]["interface"],
        })
        write_json(plugin / "source-attestation.json", {
            "source": "skill/agentmaurice",
            "version": manifest["version"],
            "content_hash": manifest["content_hash"],
            "contract_bundle_sha256": manifest["contract_bundle_sha256"],
        })
        write_json(staging / ".agents" / "plugins" / "marketplace.json", {"name": "maurice-local", "plugins": [{"name": PLUGIN_NAME, "source": "./plugins/maurice", "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL", "category": "Productivity"}}]})
        output.mkdir(parents=True, exist_ok=True)
        for path in sorted(staging.rglob("*")):
            target = output / path.relative_to(staging)
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
    archive = output / f"{PLUGIN_NAME}.plugin.tar.gz"
    with archive.open("wb") as raw, gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as compressed, tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as tar:
        plugin_root = output / "plugins" / PLUGIN_NAME
        for path in sorted(plugin_root.rglob("*")):
            if path.is_symlink():
                fail(f"symlink généré: {path}")
            if path.is_file():
                info = tar.gettarinfo(str(path), arcname=f"{PLUGIN_NAME}/{path.relative_to(plugin_root)}")
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                info.mtime = 0
                with path.open("rb") as handle:
                    tar.addfile(info, handle)
    return archive


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    archive = build(args.output, args.client)
    print(f"built {args.output / 'plugins' / PLUGIN_NAME}")
    print(f"archive {archive}")


if __name__ == "__main__":
    main()
