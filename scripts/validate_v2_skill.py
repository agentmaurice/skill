#!/usr/bin/env python3
"""Self-contained integrity gate for the distributed AgentMaurice V2 Skill."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "skill" / "agentmaurice"
MANIFEST_PATH = ROOT / "skill-version.json"
GENERATED_MANIFEST_PATH = ROOT / "references" / "generated" / "manifest.json"
FORBIDDEN = (
    "meta_recette",
    "meta-recette",
    "inception_meta_",
    "inception_recipe_",
    "deployment_alias",
    "deployment_id",
    "recipe_id",
    "recipe_call",
    "type: skill",
    "/api/v1/mcp/external/inception",
    "/Users/",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inventory(root: Path, excluded: set[Path]) -> list[dict[str, str]]:
    return [
        {"path": path.relative_to(root).as_posix(), "sha256": sha256(path.read_bytes())}
        for path in sorted(root.rglob("*"))
        if path.is_file() and path not in excluded
    ]


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    if manifest.get("schema_version") != "agentmaurice.skill/v2":
        raise SystemExit("invalid Skill schema_version")
    if manifest.get("name") != "agentmaurice" or manifest.get("version") != "2.0.2":
        raise SystemExit("invalid Skill identity")
    contract_hash = manifest.get("contract_bundle_sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", contract_hash):
        raise SystemExit("invalid contract bundle hash")

    files = inventory(ROOT, {MANIFEST_PATH})
    if manifest.get("files") != files:
        raise SystemExit("Skill file inventory or hashes are stale")
    digest = hashlib.sha256()
    for item in files:
        digest.update(f"{ROOT.name}/{item['path']}".encode())
        digest.update(b"\0")
        digest.update((ROOT / item["path"]).read_bytes())
        digest.update(b"\0")
    if manifest.get("content_hash") != digest.hexdigest():
        raise SystemExit("Skill content_hash is stale")

    generated = read_json(GENERATED_MANIFEST_PATH)
    if generated.get("contract_bundle_sha256") != contract_hash:
        raise SystemExit("generated contracts use another bundle hash")
    generated_root = GENERATED_MANIFEST_PATH.parent
    expected_generated = inventory(generated_root, {GENERATED_MANIFEST_PATH})
    if generated.get("files") != expected_generated:
        raise SystemExit("generated contract inventory or hashes are stale")

    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path == MANIFEST_PATH:
            continue
        text = path.read_text(encoding="utf-8")
        for forbidden in FORBIDDEN:
            if forbidden.lower() in text.lower():
                raise SystemExit(f"{path.relative_to(ROOT)} contains forbidden V1 surface {forbidden!r}")

    print(f"AgentMaurice Skill V2 OK: {manifest['content_hash']}")


if __name__ == "__main__":
    main()
