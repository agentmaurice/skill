#!/usr/bin/env python3
"""Self-contained integrity gate for the maurice-diagnostic Skill."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

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
# Host -> required path prefix. The host is compared exactly, never as a prefix.
ALLOWED_HOSTS = {
    "agentmaurice.ai": "/",
    "github.com": "/agentmaurice/",
    "raw.githubusercontent.com": "/agentmaurice/",
    "calendly.com": "/mikaelmorvan-agentmaurice/",
    "json-schema.org": "/",
}
SCORES = ("volume", "rules", "cost", "effort", "risk")
SOURCE_KEYS = {"agent_guide_version", "mcp_catalog_generated_at", "cib_modules_generated_at", "mode"}
OPPORTUNITY_KEYS = {"id", "title", "capability", "brick", "needs", "evidence", "scores", "pilot"}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fail(message: str) -> None:
    raise SystemExit(f"maurice-diagnostic: {message}")


def url_allowed(url: str) -> bool:
    parts = urlsplit(url)
    prefix = ALLOWED_HOSTS.get(parts.hostname or "")
    if parts.scheme != "https" or prefix is None or parts.port or parts.username:
        return False
    raw = parts.path or "/"
    if any(segment in ("..", ".") for segment in raw.split("/")) or "%2e" in raw.lower():
        return False
    return raw.startswith(prefix) or raw + "/" == prefix


def report_errors(report: dict) -> list[str]:
    """Rules of report.schema.json, checked without a third-party validator."""
    errors: list[str] = []
    required = ("schema", "generated_at", "repository", "sources", "potential", "opportunities", "anti_fit", "questions")
    for key in required:
        if key not in report:
            errors.append(f"missing {key}")
    if set(report) - set(required):
        errors.append(f"unknown keys {sorted(set(report) - set(required))}")
    if report.get("schema") != "agentmaurice.fit-diagnostic/v1":
        errors.append("schema")
    if not isinstance(report.get("generated_at"), str) or len(report["generated_at"]) < 10:
        errors.append("generated_at")
    if not isinstance(report.get("repository"), str) or not report["repository"]:
        errors.append("repository")
    for key in ("anti_fit", "questions"):
        if not isinstance(report.get(key), list) or not all(isinstance(item, str) for item in report[key]):
            errors.append(key)
    sources = report.get("sources")
    if not isinstance(sources, dict) or sources.get("mode") not in ("live", "snapshot", "mixed"):
        errors.append("sources.mode")
    elif set(sources) - SOURCE_KEYS or not all(isinstance(value, str) for value in sources.values()):
        errors.append("sources")
    potential = report.get("potential")
    if potential not in ("high", "medium", "low"):
        errors.append("potential")
    opportunities = report.get("opportunities")
    if not isinstance(opportunities, list):
        return errors + ["opportunities"]
    for index, item in enumerate(opportunities):
        where = f"opportunities[{index}]"
        if not isinstance(item, dict):
            errors.append(where)
            continue
        if set(item) != OPPORTUNITY_KEYS:
            errors.append(f"{where} keys")
        if not isinstance(item.get("title"), str) or not item["title"]:
            errors.append(f"{where}.title")
        if not re.fullmatch(r"opp-[0-9]+", str(item.get("id", ""))):
            errors.append(f"{where}.id")
        if item.get("capability") not in CAPABILITIES:
            errors.append(f"{where}.capability")
        brick = item.get("brick")
        if (
            not isinstance(brick, dict)
            or brick.get("kind") not in ("mcp", "module", "connected_service", "none")
            or set(brick) - {"kind", "ref"}
            or not isinstance(brick.get("ref", ""), str)
        ):
            errors.append(f"{where}.brick")
        if item.get("needs") not in ("maurice", "console_account", "none"):
            errors.append(f"{where}.needs")
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{where}.evidence")
        else:
            if not any(isinstance(proof, dict) and proof.get("level") == "proven" for proof in evidence):
                errors.append(f"{where}.evidence needs a proven item")
            for proof in evidence:
                if not isinstance(proof, dict) or set(proof) - {"path", "line", "level"}:
                    errors.append(f"{where}.evidence")
                    continue
                if proof.get("level") not in ("proven", "likely") or not isinstance(proof.get("path"), str) or not proof["path"]:
                    errors.append(f"{where}.evidence")
                line = proof.get("line")
                if "line" in proof and (not isinstance(line, int) or isinstance(line, bool) or line < 1):
                    errors.append(f"{where}.evidence.line")
                if proof.get("level") == "proven" and "line" not in proof:
                    errors.append(f"{where}.evidence proven without line")
        scores = item.get("scores")
        if not isinstance(scores, dict) or set(scores) != set(SCORES):
            errors.append(f"{where}.scores")
        else:
            for name in SCORES:
                value = scores[name]
                if not isinstance(value, int) or isinstance(value, bool) or not 1 <= value <= 3:
                    errors.append(f"{where}.scores.{name}")
        if not isinstance(item.get("pilot"), bool):
            errors.append(f"{where}.pilot")
    pilots = sum(1 for item in opportunities if isinstance(item, dict) and item.get("pilot") is True)
    if potential in ("high", "medium") and pilots != 1:
        errors.append(f"{potential} potential needs exactly one pilot, found {pilots}")
    if potential == "low" and pilots > 1:
        errors.append(f"low potential allows at most one pilot, found {pilots}")
    return errors


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
                if not url_allowed(url.rstrip(".,;:")):
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
    errors = report_errors(example)
    if errors or not example["opportunities"]:
        fail(f"report example is invalid: {errors}")

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
