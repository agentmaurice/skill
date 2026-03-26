---
name: agentmaurice
description: |
  Control AgentMaurice via the Workspace Control MCP gateway or the `maurice`
  CLI. Trigger this skill whenever a user mentions AgentMaurice, deployments,
  Calisto workspaces, meta-recettes, recipe definitions, drift, reconcile,
  capability contracts, External Inception, or the `maurice` CLI.
---

# AgentMaurice

Use this skill to operate AgentMaurice safely from an external AI.

Prefer the Workspace Control gateway when it is available. It gives the AI:
- session binding to a Calisto workspace
- deployment targeting
- Doctor bootstrap
- governed prepare/apply workflows
- access to expert Inception tools through `workspace_search` and `workspace_call`

If the MCP gateway is not available, fall back to the `maurice` CLI.

## Rule 1: Doctor first

Before acting on a deployment, get the Doctor contract.

Preferred bootstrap:
```text
workspace_bootstrap_contract(session_id="...", goal="update_meta_recette")
```

Manual expert path:
```text
workspace_call(tool_name="inception_deployment_doctor", arguments={"format": "ai_contract"})
```

Why:
- it reveals actual runtime capabilities
- it shows drift and current meta-recette state
- it tells the AI which workflows are allowed
- it avoids drafting specs against nonexistent tools or providers

Re-run the Doctor:
- at the start of a new task
- after apply or reconcile
- after an unexpected mutation or runtime error

## Preferred operating modes

### Mode A: Workspace Control MCP

Use this first when the connector is present.

Detection:
- `mcp__agentmaurice__workspace_search`
- `mcp__agentmaurice__workspace_call`

Key direct tools:
- `workspace_session_list`
- `workspace_session_bind`
- `workspace_bootstrap_contract`
- `workspace_current_state`
- `workspace_feature_prepare`
- `workspace_feature_apply`
- `workspace_recipe_identity_repair`

Expert access:
- `workspace_search`
- `workspace_call`

Important session tools are also reachable through expert mode, especially:
- `workspace_session_get`
- `workspace_session_list_deployments`
- `workspace_session_set_target_deployment`
- `workspace_session_prepare_apply_plan`
- `workspace_session_inspect_prepared_plan`
- `workspace_session_approve_prepared_plan`
- `workspace_session_apply_prepared_plan`
- `workspace_session_reconcile`
- `workspace_session_list_plan_approvals`

### Mode B: `maurice workspace` CLI

Use this when MCP is not connected, or when a reproducible terminal workflow is better.

Preferred bootstrap:
```bash
maurice workspace auth issue --organization <org_id>
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace tools list
```

Then call the same transparent tools as in MCP:
```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='...'
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```

### Mode C: low-level CLI or `ai run`

Use only when:
- the user explicitly wants low-level deployment tools
- workspace control is unavailable
- you need broad autonomous exploration through the internal gamemaster

## Default workflow

For a new context:
```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="...")
3. workspace_current_state()
4. If needed, use workspace_search with tool_name, then workspace_call
```

For a governed change:
```text
1. workspace_bootstrap_contract(session_id="...", goal="create_recipe|update_recipe|create_meta_recette|update_meta_recette")
2. workspace_feature_prepare(goal="...", intent_markdown="...")
3. Present the prepared plan to the user
4. workspace_feature_apply(approved_plan_hash="...")
5. workspace_current_state() or Doctor again to verify final state
```

For historical recipe identity drift:
```text
workspace_recipe_identity_repair(canonical_recipe_id="...")
```

## Tool naming rules

Recipe tools are centered on recipe definitions and executions.

Use names like:
- `inception_recipe_definitions_list`
- `inception_recipe_definitions_get`
- `inception_recipe_definitions_create`
- `inception_recipe_definitions_update`
- `inception_recipe_executions_list`

For business feature creation from user intent, prefer the meta-recette workflow over low-level recipe-definition CRUD.

## Governance rules

1. Start with the Doctor or with `workspace_bootstrap_contract`.
2. Prefer Workspace Control over low-level deployment-scoped access.
3. Identify the target deployment before mutating anything.
4. For unknown tools, use Discover, Inspect, then Call.
5. Never apply a plan without explicit user approval.
6. For production-like contexts, modify the specification, not the runtime ad hoc.
7. Re-check final state after mutations.
8. Do not mention internal company identifiers to end users.

## References

Read these only when needed:
- `references/mcp-tools.md` for current gateway and tool names
- `references/commands.md` for CLI usage
- `references/workflows.md` for common end-to-end sequences
