# Report format

Write the report in the user's language, in chat, with these sections in this
order. Keep it short: a reader should get the verdict in ten seconds and the
pilot in one minute.

````markdown
# Maurice diagnostic — <repository name>

<date> · sources: agent-guide <version>, MCP catalog <generated_at>, CIB
Modules <generated_at> (live | snapshot) · read: <N files>, skipped: <dirs> ·
read only, nothing sent

## In short
Potential: high | medium | low. Best first pilot: <title>. <One sentence on
the expected effect, qualitative only.>

## Opportunities, ranked
| # | Opportunity | Capability | Brick | Needs | Evidence | Vol. | Rules | Cost | Effort | Risk | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|

### 1. <title>
- Today: <what the code does> (`src/orders/check.py:42`)
- With Maurice: <Compiled AI Workflow / channel / MiniApp / Module …>
- Brick: <MCP slug and tool, Module key, or connected service level>
- Why it fits: <volume, rules, current cost>
- To confirm: <what the code cannot tell>

## Recommended first pilot
Scope, inputs and outputs, a measurable success criterion (cost per run,
latency, accuracy on the exact rules), and what stays out of scope.

## Where Maurice brings nothing here
<anti-signals found, plainly>

## Questions for the team
<hypotheses and missing context>

## Next steps
1. Install Maurice from this assistant
2. `maurice doctor --json`
3. Give the block below to the `agentmaurice` Skill to build the pilot
4. Demo: https://calendly.com/mikaelmorvan-agentmaurice/30min

## Machine block
```json
{ ... }
```
````

## Machine block

The block validates against [report.schema.json](report.schema.json)
(`agentmaurice.fit-diagnostic/v1`). Example:

```json
{
  "schema": "agentmaurice.fit-diagnostic/v1",
  "generated_at": "2026-10-19",
  "repository": "acme-orders",
  "sources": {
    "agent_guide_version": "1.4.0",
    "mcp_catalog_generated_at": "2026-10-01T08:59:19Z",
    "cib_modules_generated_at": "2026-10-19",
    "mode": "live"
  },
  "potential": "high",
  "opportunities": [
    {
      "id": "opp-1",
      "title": "Compile the order compliance check",
      "capability": "compiled_workflow",
      "brick": { "kind": "mcp", "ref": "decision" },
      "needs": "maurice",
      "evidence": [{ "path": "src/orders/check.py", "line": 42, "level": "proven" }],
      "scores": { "volume": 3, "rules": 3, "cost": 3, "effort": 2, "risk": 2 },
      "pilot": true
    }
  ],
  "anti_fit": ["Real-time pricing loop needs sub-second latency"],
  "questions": ["How many orders are checked per day?"]
}
```

Allowed `capability` values: `compiled_workflow`, `workflow`, `agent_mode`,
`channel`, `miniapp`, `human_approval`, `vault`, `mcp`, `swarm`,
`organisation`, `module`, `connected_service`, `entry_point`.
Allowed `brick.kind`: `mcp`, `module`, `connected_service`, `none`. With
`mcp`, `ref` is a `slug` of the MCP catalog; with `module`, a Module `key`.
An MCP server that already lives in the analysed repository is not a brick:
use `capability: "mcp"` with `brick.kind: "none"`.
Allowed `needs`: `maurice`, `console_account`, `none`.
Allowed `evidence.level`: `proven` (requires `line`), `likely`
(`hypothesis` items go to `questions`). Every opportunity has at least one
`proven` evidence; `likely` items only add context. When the potential is `high` or
`medium`, exactly one opportunity has `"pilot": true`; when it is `low`, at
most one does.
