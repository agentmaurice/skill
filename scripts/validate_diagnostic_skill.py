#!/usr/bin/env python3
"""Self-contained integrity gate for the maurice-diagnostic Skill."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "skill" / "maurice-diagnostic"
MANIFEST_PATH = ROOT / "skill-version.json"
CIB_PUBLIC = REPO / "scripts" / "diagnostic" / "cib-public.json"
FORBIDDEN = (
    "kraftek",
    "chatserver",
    "recipe",
    "/Users/",
    "localhost",
    "127.0.0.1",
    "inference swarm",
    "réseau de maurice",
    "open source",
)
REQUIRED_SKILL = (
    "Read only.",
    "Never open `.env`",
    "path:line",
    "maurice doctor --json",
    "agentmaurice.fit-diagnostic/v1",
)
CAPABILITIES = {
    "compiled_workflow", "workflow", "agent_mode", "channel", "miniapp", "human_approval",
    "vault", "mcp", "swarm", "organisation", "module", "connected_service", "entry_point",
}
ALLOWED_URL = re.compile(
    r"https://(agentmaurice\.ai|github\.com/agentmaurice|raw\.githubusercontent\.com/agentmaurice"
    r"|calendly\.com/mikaelmorvan-agentmaurice|json-schema\.org)[^\s)`\"']*"
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"maurice-diagnostic: {message}")


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != "agentmaurice.skill/v2" or manifest.get("name") != "maurice-diagnostic":
        fail("invalid Skill identity")
    if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.get("version", "")):
        fail("invalid version")

    files = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path.read_bytes())}
        for path in sorted(ROOT.rglob("*"))
        if path.is_file() and path != MANIFEST_PATH
    ]
    if manifest.get("files") != files:
        fail("file inventory or hashes are stale: run scripts/generate_diagnostic_snapshots.py --manifest-only")
    digest = hashlib.sha256()
    for item in files:
        digest.update(f"{ROOT.name}/{item['path']}".encode())
        digest.update(b"\0")
        digest.update((ROOT / item["path"]).read_bytes())
        digest.update(b"\0")
    if manifest.get("content_hash") != digest.hexdigest():
        fail("content_hash is stale")

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        for forbidden in FORBIDDEN:
            if forbidden.lower() in lowered:
                fail(f"{path.relative_to(ROOT)} contains forbidden term {forbidden!r}")
        if path.suffix == ".md":
            for url in re.findall(r"https?://[^\s)`\"'>]+", text):
                if not ALLOWED_URL.fullmatch(url):
                    fail(f"{path.relative_to(ROOT)} links outside public AgentMaurice sources: {url}")
            for link in re.findall(r"\]\(([^)#]+)\)", text):
                if not link.startswith("http") and not (path.parent / link).exists():
                    fail(f"{path.relative_to(ROOT)} has a broken relative link {link}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\nname: maurice-diagnostic\ndescription: "):
        fail("SKILL.md front matter must start with name and description")
    for required in REQUIRED_SKILL:
        if required not in skill and required not in (ROOT / "references" / "report-format.md").read_text(encoding="utf-8"):
            fail(f"missing required guidance {required!r}")

    schema = json.loads((ROOT / "references" / "report.schema.json").read_text(encoding="utf-8"))
    enum = set(schema["properties"]["opportunities"]["items"]["properties"]["capability"]["enum"])
    if enum != CAPABILITIES:
        fail("report schema capability enum drifted")
    report_format = (ROOT / "references" / "report-format.md").read_text(encoding="utf-8")
    example = json.loads(re.search(r"Example:\n\n```json\n(.*?)\n```", report_format, re.S).group(1))
    if example["schema"] != "agentmaurice.fit-diagnostic/v1" or not example["opportunities"]:
        fail("report example is invalid")
    for opportunity in example["opportunities"]:
        if opportunity["capability"] not in CAPABILITIES or not opportunity["evidence"]:
            fail("report example opportunity is invalid")

    mcp = json.loads((ROOT / "references" / "generated" / "mcp-catalog.json").read_text(encoding="utf-8"))
    if mcp.get("schema_version") != "agentmaurice.diagnostic.mcp-catalog/v1" or not mcp.get("servers"):
        fail("MCP snapshot is invalid")
    grid = (ROOT / "references" / "capability-grid.md").read_text(encoding="utf-8")
    for server in mcp["servers"]:
        if f"`{server['slug']}`" not in grid:
            fail(f"MCP server {server['slug']!r} is missing from the capability grid")

    cib = json.loads((ROOT / "references" / "generated" / "cib-modules.json").read_text(encoding="utf-8"))
    public = json.loads(CIB_PUBLIC.read_text(encoding="utf-8"))["modules"]
    keys = [module["key"] for module in cib.get("modules", [])]
    if cib.get("schema_version") != "agentmaurice.diagnostic.cib-modules/v1" or sorted(keys) != sorted(public):
        fail("CIB snapshot and cib-public.json differ")
    for key in keys:
        if f"`{key}`" not in grid:
            fail(f"Module {key!r} is missing from the capability grid")

    print(f"maurice-diagnostic Skill OK: {manifest['version']} {manifest['content_hash']}")


if __name__ == "__main__":
    main()
