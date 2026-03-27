# Verify a Recipe Backend

Use this when you want the AI to confirm that an AgentMaurice deployment behaves like a workflow backend for `mode=recipe` recipes.

## Prompt

```text
Use $agentmaurice to verify this AgentMaurice recipe backend.
Start with the Doctor contract, confirm which recipe definitions are active,
then run the lightest useful verification path for one target recipe.
If a direct runtime check is possible, execute or start the recipe and inspect the status.
Do not apply any governed change.
```

## Expected MCP Path

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
4. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
5. workspace_call(tool_name="inception_recipe_definitions_get", arguments={"id":"<recipe_id>"})
6. If a live execution exists or is started, workspace_call(tool_name="inception_recipe_executions_get", arguments={"id":"<execution_id>"})
```

## Expected CLI and HTTP Path

```bash
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract
maurice workspace call workspace_current_state
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_recipe_definitions_list --deployment <id>
maurice tools call inception_recipe_definitions_get --deployment <id> --arg id=<recipe_id>

# Optional direct backend execution check with a deployment API key
curl -X POST \
  -H "Authorization: Bearer <deployment_api_key>" \
  -H "Content-Type: application/json" \
  <base_url>/recipe/<deployment_id>/<recipe_id>/execute \
  -d '{"input":{}}'
```

## Verification Goals

- confirm the target recipe is in `mode=recipe`
- confirm the deployment exposes the recipe backend surface
- confirm execution status, logs, or trace are readable when a run is started
