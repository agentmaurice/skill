#!/usr/bin/env python3
"""Assemble the GitHub catalog from CI-built native connectors; no local build at install."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from build_client_plugin import build, write_json, assert_output, CONNECTED_PLUGIN_VERSION


def catalog(output: Path, connectors: Path, source_commit: str) -> None:
    assert_output(output)
    if len(source_commit) != 40 or any(c not in '0123456789abcdef' for c in source_commit):
        raise SystemExit('source commit must be a complete Git SHA')
    with tempfile.TemporaryDirectory(prefix='maurice-catalog-') as tmp:
        staging = Path(tmp) / 'catalog'
        staging.mkdir()
        for client in ('codex', 'claude'):
            generated = Path(tmp) / client
            archive = build(generated, client, connectors)
            shutil.copytree(generated / 'plugins/maurice', staging / 'plugins' / client / 'maurice')
            shutil.copyfile(archive, staging / f'maurice-{client}-{CONNECTED_PLUGIN_VERSION}.tar.gz')
        write_json(staging / '.agents/plugins/marketplace.json', {
            'name': 'agentmaurice', 'interface': {'displayName': 'AgentMaurice'},
            'plugins': [{'name': 'maurice', 'source': {'source': 'local', 'path': './plugins/codex/maurice'},
                         'policy': {'installation': 'AVAILABLE', 'authentication': 'ON_INSTALL', 'category': 'Productivity'}}],
        })
        write_json(staging / '.claude-plugin/marketplace.json', {
            'name': 'agentmaurice', 'owner': {'name': 'AgentMaurice'},
            'plugins': [{'name': 'maurice', 'source': './plugins/claude/maurice'}],
        })
        (staging / 'README.md').write_text(
            '# Maurice — plugins prêts à installer\n\n'
            'Ce catalogue contient les connecteurs natifs, les instructions et leurs attestations. '
            'Il ne contient pas le runtime One.\n\n'
            'Codex : `codex plugin marketplace add agentmaurice/skill --ref plugins`, '
            'puis `codex plugin add maurice@agentmaurice`.\n\n'
            'Claude Code : `/plugin install maurice --marketplace agentmaurice/skill#plugins`.\n\n'
            'Puis demander : **Connecte Maurice à mon One.** '
            'Indiquer son adresse et autoriser dans One. Aucun secret à copier.\n\n'
            'Sources et documentation : https://github.com/agentmaurice/skill\n', encoding='utf-8')
        files = {str(p.relative_to(staging)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(staging.rglob('*')) if p.is_file()}
        write_json(staging / 'release.json', {'schema': 'agentmaurice.plugin_release/v1',
            'version': CONNECTED_PLUGIN_VERSION, 'source_repository': 'https://github.com/agentmaurice/skill',
            'source_commit': source_commit, 'pairing_contract': 'agentmaurice.assistant_pairing/v1', 'files': files})
        (staging / 'SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name, digest in files.items()), encoding='utf-8')
        shutil.copytree(staging, output, dirs_exist_ok=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--connector-dir', required=True, type=Path)
    p.add_argument('--source-commit', required=True)
    a = p.parse_args()
    catalog(a.output, a.connector_dir, a.source_commit)
