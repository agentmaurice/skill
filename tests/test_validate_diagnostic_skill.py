"""Cases found by the adversarial review of AGENT-985."""

import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_diagnostic_skill as gate  # noqa: E402

FORMAT = (ROOT / "skill" / "maurice-diagnostic" / "references" / "report-format.md").read_text(encoding="utf-8")
EXAMPLE = json.loads(re.search(r"Example:\n\n```json\n(.*?)\n```", FORMAT, re.S).group(1))


def report(**changes):
    value = copy.deepcopy(EXAMPLE)
    value.update(changes)
    return value


class ReportRules(unittest.TestCase):
    def test_published_example_is_valid(self):
        self.assertEqual(gate.report_errors(EXAMPLE), [])

    def test_proven_evidence_needs_a_line(self):
        value = report()
        value["opportunities"][0]["evidence"] = [{"path": "src/orders/check.py", "level": "proven"}]
        self.assertIn("opportunities[0].evidence proven without line", gate.report_errors(value))

    def test_high_potential_needs_exactly_one_pilot(self):
        none = report()
        none["opportunities"][0]["pilot"] = False
        self.assertTrue(any("exactly one pilot" in e for e in gate.report_errors(none)))
        two = report()
        second = copy.deepcopy(two["opportunities"][0])
        second["id"] = "opp-2"
        two["opportunities"].append(second)
        self.assertTrue(any("exactly one pilot" in e for e in gate.report_errors(two)))

    def test_low_potential_allows_no_pilot(self):
        value = report(potential="low")
        value["opportunities"][0]["pilot"] = False
        self.assertEqual(gate.report_errors(value), [])

    def test_scores_out_of_range_and_missing_sources_fail(self):
        value = report()
        value["opportunities"][0]["scores"]["volume"] = 99
        del value["sources"]
        errors = gate.report_errors(value)
        self.assertIn("opportunities[0].scores.volume", errors)
        self.assertIn("missing sources", errors)


class ReportRulesSecondReview(unittest.TestCase):
    def test_likely_only_evidence_is_refused(self):
        value = report()
        value["opportunities"][0]["evidence"] = [{"path": "src/inexistant.py", "level": "likely"}]
        self.assertIn("opportunities[0].evidence needs a proven item", gate.report_errors(value))

    def test_wrong_types_and_missing_title_are_refused(self):
        value = report(generated_at=None, repository=[], anti_fit="aucun")
        del value["opportunities"][0]["title"]
        errors = gate.report_errors(value)
        for expected in ("generated_at", "repository", "anti_fit", "opportunities[0].title", "opportunities[0] keys"):
            self.assertIn(expected, errors)

    def test_grid_never_asks_to_invent_a_tool_name(self):
        grid = (ROOT / "skill" / "maurice-diagnostic" / "references" / "capability-grid.md").read_text(encoding="utf-8")
        self.assertIn("never invent", grid)
        self.assertIn("`tools` list is empty", grid)


class UrlAllowList(unittest.TestCase):
    def test_lookalike_hosts_are_refused(self):
        for url in (
            "https://agentmaurice.ai.evil.example/",
            "https://evil.example/agentmaurice.ai",
            "https://github.com/agentmaurice-evil/skill",
            "https://raw.githubusercontent.com/someone/agentmaurice/x",
            "http://agentmaurice.ai/",
            "https://agentmaurice.ai:8443/",
        ):
            self.assertFalse(gate.url_allowed(url), url)

    def test_public_sources_are_allowed(self):
        for url in (
            "https://agentmaurice.ai/skill/maurice-diagnostic/SKILL.md",
            "https://github.com/agentmaurice/mcp",
            "https://raw.githubusercontent.com/agentmaurice/mcp/main/catalog.json",
            "https://calendly.com/mikaelmorvan-agentmaurice/30min",
        ):
            self.assertTrue(gate.url_allowed(url), url)


class UrlLaunch(unittest.TestCase):
    def test_skill_resolves_references_against_the_published_base(self):
        skill = (ROOT / "skill" / "maurice-diagnostic" / "SKILL.md").read_text(encoding="utf-8")
        sources = (ROOT / "skill" / "maurice-diagnostic" / "references" / "sources.md").read_text(encoding="utf-8")
        self.assertIn("https://agentmaurice.ai/skill/maurice-diagnostic/", skill)
        self.assertIn("This Skill's own files are also allowed", sources)


if __name__ == "__main__":
    unittest.main()
