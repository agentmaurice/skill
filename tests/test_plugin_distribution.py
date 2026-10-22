from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build_client_plugin import build
from build_plugin_catalog import catalog


class PluginDistribution(unittest.TestCase):
    def fixture(self, root):
        for target in ('darwin-arm64', 'darwin-amd64', 'linux-amd64', 'linux-arm64', 'windows-amd64'):
            path = root / target / ('maurice-connector.exe' if target.startswith('windows') else 'maurice-connector')
            path.parent.mkdir(parents=True)
            path.write_text('#!/bin/sh\nprintf "%s\\n" "connector-fixture"\n')
        return root

    def test_catalog_has_native_connectors_and_private_pairing_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            output = base / 'out'
            catalog(output, self.fixture(base / 'connectors'), 'a' * 40)
            for client in ('codex', 'claude'):
                plugin = output / 'plugins' / client / 'maurice'
                manifest = json.loads((plugin / 'plugin.json').read_text())
                self.assertEqual(manifest['version'], '0.2.1')
                mcp = json.loads((plugin / 'mcp.json').read_text())['mcpServers']['maurice']
                self.assertEqual(mcp['args'], ['--client', 'codex' if client == 'codex' else 'claude-code'])
                self.assertEqual(mcp['command'], './bin/maurice-connector')
                self.assertNotIn('env', mcp)
                attestation = json.loads((plugin / 'connector-attestation.json').read_text())
                self.assertEqual(attestation['version'], '0.2.1')
                for name, digest in attestation['files'].items():
                    self.assertEqual(hashlib.sha256((plugin / name).read_bytes()).hexdigest(), digest)
                    self.assertTrue((plugin / name).stat().st_mode & stat.S_IXUSR)
                if os.name != 'nt':
                    run = subprocess.run([str(plugin / 'bin/maurice-connector'), '--version'], capture_output=True, text=True)
                    self.assertEqual(run.returncode, 0, run.stderr)
                    self.assertEqual(run.stdout.strip(), 'connector-fixture')
                setup = (plugin / 'skills/setup/SKILL.md').read_text()
                self.assertIn('maurice.connection_check', setup)
                self.assertIn('Ne jamais approuver', setup)
                for source in (ROOT / 'skill/agentmaurice').rglob('*'):
                    if source.is_file():
                        self.assertEqual(source.read_bytes(), (plugin / 'skills/agentmaurice' / source.relative_to(ROOT / 'skill/agentmaurice')).read_bytes())
            codex = json.loads((output / '.agents/plugins/marketplace.json').read_text())
            claude = json.loads((output / '.claude-plugin/marketplace.json').read_text())
            self.assertEqual(codex['plugins'][0]['source']['path'], './plugins/codex/maurice')
            self.assertEqual(claude['plugins'][0]['source'], './plugins/claude/maurice')
            catalog_readme = (output / 'README.md').read_text()
            self.assertIn('--ref catalog', catalog_readme)
            self.assertIn('agentmaurice/skill#catalog', catalog_readme)
            self.assertNotIn('--ref plugins', catalog_readme)
            self.assertNotIn('agentmaurice/skill#plugins', catalog_readme)
            release = json.loads((output / 'release.json').read_text())
            self.assertEqual(release['version'], '0.2.1')
            self.assertEqual(release['source_commit'], 'a' * 40)
            self.assertEqual(set(release['files']), {str(p.relative_to(output)) for p in output.rglob('*') if p.is_file()} - {'release.json', 'SHA256SUMS'})
            for name, digest in release['files'].items():
                self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)

    def test_incomplete_or_symlinked_connector_is_not_published(self):
        for kind in ('missing', 'symlink'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                connectors = self.fixture(base / 'connectors')
                source = connectors / 'linux-arm64/maurice-connector'
                source.unlink()
                if kind == 'symlink':
                    source.symlink_to(connectors / 'linux-amd64/maurice-connector')
                with self.assertRaises(SystemExit):
                    catalog(base / 'out', connectors, 'a' * 40)
                self.assertFalse((base / 'out').exists())

    def test_catalog_requires_real_source_revision(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                catalog(Path(tmp) / 'out', Path(tmp) / 'unused', 'main')


if __name__ == '__main__':
    unittest.main()
