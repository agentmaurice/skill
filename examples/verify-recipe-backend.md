# Verify a Recipe Backend

Use this when you want the AI to confirm that an AgentMaurice deployment behaves
like a workflow backend for `mode=recipe` recipes.

## Prompt

```text
Use $agentmaurice to verify this AgentMaurice recipe backend.
Start with deployment scopes and Doctor, confirm which recipe is active, then
run the lightest useful observed execution. Return status, result, trace_id,
logs/traces summary, and usage_summary. Do not apply any governed change.
```

## Expected External Inception Path

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
3. inception_call(tool_name="inception_mcp_capabilities", arguments={"deployment_alias":"support"})
4. inception_call(tool_name="inception_recipe_run_observed", arguments={
     "deployment_alias":"support",
     "recipe_id":"recipe_x",
     "logs_limit":50,
     "trace_limit":50,
     "include_otel_trace":true
   })
5. inception_call(tool_name="inception_recipe_execution_usage", arguments={
     "deployment_alias":"support",
     "execution_id":"exec_x"
   })
```

## Expected CLI and HTTP Path

```bash
maurice tools call inception_deployment_doctor --deployment <deployment_id> --arg format=ai_contract
maurice tools call inception_recipe_definitions_list --deployment <deployment_id>
maurice tools call inception_recipe_definitions_get --deployment <deployment_id> --arg id=<recipe_id>
maurice tools call inception_recipe_run_observed --deployment <deployment_id> --arg recipe_id=<recipe_id> --arg logs_limit=50 --arg trace_limit=50
maurice tools call inception_recipe_execution_usage --deployment <deployment_id> --arg execution_id=<execution_id>

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
- confirm execution state, result, logs, traces and `trace_id`
- report `usage_summary.duration_ms`, actions, LLM tokens, estimated cost and
  metering source when available
- compare multiple runs with `inception_recipe_execution_usage` when the user
  is optimizing a recipe
