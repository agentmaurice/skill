#!/usr/bin/env python3
"""Refresh the maurice-diagnostic snapshots and its file inventory.

Sources: the public MCP catalog (GitHub) and the Company in a Box Modules
inventory (sibling checkout), merged with the public summaries kept in
scripts/diagnostic/cib-public.json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skill" / "maurice-diagnostic"
GENERATED = ROOT / "references" / "generated"
MANIFEST = ROOT / "skill-version.json"
VERSION = "0.1.0"
MCP_CATALOG_URL = "https://raw.githubusercontent.com/agentmaurice/mcp/main/catalog.json"
CIB_PUBLIC = REPO / "scripts" / "diagnostic" / "cib-public.json"


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def mcp_snapshot(source: str) -> dict:
    if source.startswith("https://"):
        request = urllib.request.Request(source, headers={"User-Agent": "maurice-diagnostic-generator"})
        raw = urllib.request.urlopen(request, timeout=30).read()
    else:
        raw = Path(source).read_bytes()
    catalog = json.loads(raw)
    if catalog.get("schema_version") != "agentmaurice.mcp-catalog/v1":
        raise SystemExit("unexpected MCP catalog schema")
    servers = [
        {
            "slug": server["slug"],
            "version": server["version"],
            "description": server["description"],
            "one_compatible": server["one_compatible"],
            "tags": server.get("tags", []),
            "tools": [{"name": tool["name"], "description": tool["description"]} for tool in server.get("tools", [])],
        }
        for server in catalog["servers"]
        if server.get("kind") == "server"
    ]
    return {
        "schema_version": "agentmaurice.diagnostic.mcp-catalog/v1",
        "generated_at": catalog["generated_at"],
        "repository": catalog["repository"],
        "live_url": MCP_CATALOG_URL,
        "servers": servers,
    }


def cib_snapshot(cib_dir: Path, generated_at: str) -> dict:
    inventory = json.loads((cib_dir / "modules.json").read_text(encoding="utf-8"))
    public = json.loads(CIB_PUBLIC.read_text(encoding="utf-8"))["modules"]
    keys = [module["key"] for module in inventory["modules"]]
    if sorted(keys) != sorted(public):
        raise SystemExit(f"cib-public.json and modules.json differ: {sorted(set(keys) ^ set(public))}")
    revision = subprocess.run(
        ["git", "-C", str(cib_dir), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    modules = []
    for module in inventory["modules"]:
        manifest = json.loads((cib_dir / module["manifest"]).read_text(encoding="utf-8"))
        modules.append(
            {
                "key": module["key"],
                "name": manifest.get("name", module["key"]),
                "version": module["version"],
                "workflows": module["workflows"],
                "miniapps": module["miniapps"],
                **public[module["key"]],
            }
        )
    return {
        "schema_version": "agentmaurice.diagnostic.cib-modules/v1",
        "generated_at": generated_at,
        "source_revision": revision,
        "installation": "Guided: composed into the consuming project, then deployed through the Agent Spec rail. Installation by URL is not offered.",
        "not_delivered": ["HR", "Sales", "sector-specific packs"],
        "modules": modules,
    }


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory() -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path.read_bytes())}
        for path in sorted(ROOT.rglob("*"))
        if path.is_file() and path != MANIFEST
    ]


def content_hash(files: list[dict[str, str]]) -> str:
    digest = hashlib.sha256()
    for item in files:
        digest.update(f"{ROOT.name}/{item['path']}".encode())
        digest.update(b"\0")
        digest.update((ROOT / item["path"]).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def write_manifest() -> None:
    files = inventory()
    write_json(
        MANIFEST,
        {
            "schema_version": "agentmaurice.skill/v2",
            "name": "maurice-diagnostic",
            "version": VERSION,
            "content_hash": content_hash(files),
            "files": files,
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-catalog", default=MCP_CATALOG_URL, help="URL or path of catalog.json")
    parser.add_argument("--cib-dir", type=Path, default=REPO.parent / "company-in-a-box-modules")
    parser.add_argument("--date", default=dt.date.today().isoformat(), help="generated_at of the CIB snapshot")
    parser.add_argument("--manifest-only", action="store_true", help="only refresh skill-version.json")
    args = parser.parse_args()
    if not args.manifest_only:
        write_json(GENERATED / "mcp-catalog.json", mcp_snapshot(args.mcp_catalog))
        write_json(GENERATED / "cib-modules.json", cib_snapshot(args.cib_dir.resolve(), args.date))
    write_manifest()
    print(f"maurice-diagnostic {VERSION} snapshots and inventory refreshed")


if __name__ == "__main__":
    main()
