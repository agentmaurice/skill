#!/usr/bin/env python3
"""Build a self-contained Agent Plugins 1.0 package for a supported client."""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import hashlib
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "skill" / "agentmaurice"
PLUGIN_NAME = "maurice"
PLUGIN_VERSION = "0.1.0"
CONNECTED_PLUGIN_VERSION = "0.2.0"
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


def validate_guide_links(guides: Path, package_root: Path) -> None:
    package_root = package_root.resolve()
    for guide in guides.rglob("*.md"):
        text = guide.read_text(encoding="utf-8")
        relative = guide.resolve().relative_to(package_root)
        for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            parsed = urlparse(link)
            if not parsed.path or parsed.scheme or link.startswith("//"):
                continue
            destination = (guide.parent / parsed.path).resolve()
            if not destination.is_relative_to(package_root):
                fail(f"lien de guide hors paquet: {relative} -> {link}")
            if not destination.is_file():
                fail(f"lien de guide cassé: {relative} -> {link}")


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def package_connector(plugin: Path, connector_dir: Path, client: str) -> None:
    """Copy CI-built executables; installation never builds or downloads code."""
    if not connector_dir.is_dir() or connector_dir.is_symlink():
        fail("--connector-dir doit désigner les binaires construits par la CI")
    ensure_no_symlinks(connector_dir)
    hashes = {}
    for platform in ("darwin-arm64", "darwin-amd64", "linux-amd64", "linux-arm64", "windows-amd64"):
        name = "maurice-connector.exe" if platform.startswith("windows-") else "maurice-connector"
        source = connector_dir / platform / name
        if not source.is_file() or source.stat().st_size == 0:
            fail(f"connecteur absent ou vide pour {platform}")
        target = plugin / "bin" / platform / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        target.chmod(0o755)
        hashes[str(target.relative_to(plugin))] = hashlib.sha256(target.read_bytes()).hexdigest()
    launcher = plugin / "bin" / "maurice-connector"
    launcher.write_text('''#!/bin/sh
set -eu
case "$(uname -s):$(uname -m)" in
  Darwin:arm64) platform=darwin-arm64 ;;
  Darwin:x86_64) platform=darwin-amd64 ;;
  Linux:aarch64|Linux:arm64) platform=linux-arm64 ;;
  Linux:x86_64|Linux:amd64) platform=linux-amd64 ;;
  *) echo 'Maurice: unsupported platform; use a supported native package.' >&2; exit 1 ;;
esac
base=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec "$base/$platform/maurice-connector" "$@"
''', encoding="utf-8")
    launcher.chmod(0o755)
    # Windows CreateProcess resolves the extensionless command to this .exe.
    shutil.copyfile(plugin / "bin/windows-amd64/maurice-connector.exe", plugin / "bin/maurice-connector.exe")
    (plugin / "bin/maurice-connector.exe").chmod(0o755)
    for path in (launcher, plugin / "bin/maurice-connector.exe"):
        hashes[str(path.relative_to(plugin))] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_json(plugin / "connector-attestation.json", {
        "schema": "agentmaurice.connector_distribution/v1",
        "version": CONNECTED_PLUGIN_VERSION,
        "files": hashes,
    })
    native_client = "claude-code" if client == "claude" else "codex"
    server = {"type": "stdio", "command": "${PLUGIN_ROOT}/bin/maurice-connector", "args": ["--client", native_client]}
    write_json(plugin / "mcp.json", {
        "$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json",
        "mcpServers": {"maurice": server},
    })
    write_json(plugin / ".mcp.json", {"mcpServers": {"maurice": {
        **server, "command": "${CLAUDE_PLUGIN_ROOT}/bin/maurice-connector",
    }}})
    setup = plugin / "skills/setup"
    setup.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "plugins/shared/setup/SKILL.md", setup / "SKILL.md")


def build_codex(output: Path, connector_dir: Path | None = None) -> Path:
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
            "version": CONNECTED_PLUGIN_VERSION if connector_dir else PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {"name": "AgentMaurice"},
            "license": "Proprietary",
            "keywords": ["agentmaurice", "workflow", "mcp"],
            "extensions": {"com.openai": {"interface": {"displayName": "Maurice", "developerName": "AgentMaurice", "shortDescription": "Workflows AgentMaurice", "category": "Productivity"}}},
        }
        if connector_dir:
            package_connector(plugin, connector_dir, "codex")
            portable_manifest["extensions"]["com.openai"]["onboardingSkill"] = "./skills/setup/SKILL.md"
        write_json(plugin / "plugin.json", portable_manifest)
        write_json(plugin / ".codex-plugin" / "plugin.json", {
            "name": PLUGIN_NAME,
            "version": portable_manifest["version"],
            "description": PLUGIN_DESCRIPTION,
            "author": {"name": "AgentMaurice"},
            "skills": "./skills/",
            "interface": portable_manifest["extensions"]["com.openai"]["interface"],
            **({"mcpServers": "./.mcp.json", "extensions": {"com.openai": {"onboardingSkill": "./skills/setup/SKILL.md"}}} if connector_dir else {}),
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
                target.chmod(path.stat().st_mode & 0o777)
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


def build_claude(output: Path, connector_dir: Path | None = None) -> Path:
    manifest = validate_canonical()
    assert_output(output)
    template_root = ROOT / "plugins" / "claude" / "maurice"
    if not template_root.is_dir() or template_root.is_symlink():
        fail("template Claude maurice introuvable")
    ensure_no_symlinks(ROOT / "plugins" / "claude")
    template = template_root / "SKILL.md"
    if not template.is_file():
        fail("template Claude maurice introuvable")
    with tempfile.TemporaryDirectory(prefix="agentmaurice-plugin-") as temp:
        staging = Path(temp) / "output"
        plugin = staging / "plugins" / PLUGIN_NAME
        copy_tree(CANONICAL, plugin / "skills" / "agentmaurice")
        readme = ROOT / "plugins" / "claude" / "README.md"
        if not readme.is_file() or readme.is_symlink():
            fail("README Claude introuvable")
        shutil.copyfile(readme, plugin / "README.md")
        copy_tree(template_root, plugin / "skills" / "maurice")
        validate_guide_links(plugin / "skills" / "maurice", plugin)
        if connector_dir:
            package_connector(plugin, connector_dir, "claude")
        write_json(plugin / "plugin.json", {
            "$schema": PLUGIN_SCHEMA,
            "name": PLUGIN_NAME,
            "version": CONNECTED_PLUGIN_VERSION if connector_dir else PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {"name": "AgentMaurice"},
            "license": "Proprietary",
            "keywords": ["agentmaurice", "workflow", "mcp"],
        })
        write_json(plugin / ".claude-plugin" / "plugin.json", {
            "name": PLUGIN_NAME,
            "version": CONNECTED_PLUGIN_VERSION if connector_dir else PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {"name": "AgentMaurice"},
            "license": "Proprietary",
        })
        write_json(plugin / "source-attestation.json", {
            "source": "skill/agentmaurice",
            "version": manifest["version"],
            "content_hash": manifest["content_hash"],
            "contract_bundle_sha256": manifest["contract_bundle_sha256"],
        })
        write_json(staging / ".claude-plugin" / "marketplace.json", {
            "name": "maurice-local",
            "owner": {"name": "AgentMaurice"},
            "plugins": [{"name": PLUGIN_NAME, "source": "./plugins/maurice"}],
        })
        output.mkdir(parents=True, exist_ok=True)
        for path in sorted(staging.rglob("*")):
            target = output / path.relative_to(staging)
            if path.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
                target.chmod(path.stat().st_mode & 0o777)
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


def build(output: Path, client: str, connector_dir: Path | None = None) -> Path:
    if client == "codex":
        return build_codex(output, connector_dir)
    if client == "claude":
        return build_claude(output, connector_dir)
    fail("client non supporté: choisir codex ou claude")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--client", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--connector-dir", type=Path, help="CI-built native executables for the connected distribution")
    args = parser.parse_args()
    archive = build(args.output, args.client, args.connector_dir)
    print(f"built {args.output / 'plugins' / PLUGIN_NAME}")
    print(f"archive {archive}")


if __name__ == "__main__":
    main()
