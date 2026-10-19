# Sources

Fetch the live sources first. They are public and need no account. If one is
unreachable, use the snapshot and print its `generated_at` date in the report
header.

| Source | Live URL | Snapshot |
|---|---|---|
| Concepts, availability, install routes | https://agentmaurice.ai/agent-guide/v1.json (compact: https://agentmaurice.ai/llms.txt) | — (use the grid) |
| AgentMaurice MCP servers | https://raw.githubusercontent.com/agentmaurice/mcp/main/catalog.json (repository: https://github.com/agentmaurice/mcp) | `generated/mcp-catalog.json` |
| Company in a Box Modules | https://agentmaurice.ai/skill/maurice-diagnostic/references/generated/cib-modules.json | `generated/cib-modules.json` |
| Connected services (Console) | not published yet | — |

## How to use them

- `agent-guide/v1.json` is authoritative for what is available. If it marks a
  capability as not available or coming soon, do not recommend it.
- `catalog.json` (`agentmaurice.mcp-catalog/v1`): per server `slug`,
  `version`, `description`, `tools`, `tags`, `one_compatible`. Match tags and
  descriptions to the signals; cite the slug.
- `cib-modules.json` (`agentmaurice.diagnostic.cib-modules/v1`): per Module
  `key`, `version`, `summary`, `use_when`, Workflow and MiniApp counts.
- Connected services: until the integrations catalog is published, a SaaS SDK
  found in the code gives "connectable through the Console, to be checked";
  name the SDK and the provider, nothing more.

This Skill's own files are also allowed: when you read `SKILL.md` from
https://agentmaurice.ai/skill/maurice-diagnostic/SKILL.md, load each
reference from the same base URL, for example
https://agentmaurice.ai/skill/maurice-diagnostic/references/capability-grid.md
(the editorial copy is https://github.com/agentmaurice/skill under
`skill/maurice-diagnostic/`).

Do not fetch any other URL, and never send repository content anywhere.
