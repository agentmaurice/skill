# Verify a Mini-App and OpenUI Backend

Use this when you want the AI to confirm that an AgentMaurice deployment behaves like an interactive backend for `mode=app` recipes and that OpenUI delivery is wired correctly.

## Prompt

```text
Use $agentmaurice to verify this AgentMaurice mini-app backend.
Start with the Doctor contract, confirm that the deployment exposes app-mode recipes,
check the viewer bootstrap, then verify the OpenUI delivery path and its native fallback.
If a draft meta-recette is under review, prefer the preview endpoints before touching the live runtime.
Do not apply any governed change.
```

## Expected MCP Path

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
4. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
5. Use the Doctor mini-app preview endpoints when a draft meta-recette exists
6. Otherwise use the runtime viewer and app-instance HTTP endpoints
```

## Expected CLI and HTTP Path

```bash
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract
maurice workspace call workspace_current_state
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_recipe_definitions_list --deployment <id>

# Viewer bootstrap
curl -H "Authorization: Bearer <deployment_api_key>" \
  <base_url>/viewer/<deployment_id>

# Optional live mini-app runtime check
curl -X POST \
  -H "Authorization: Bearer <deployment_api_key>" \
  -H "Content-Type: application/json" \
  <base_url>/app/<deployment_id>/<recipe_id>/instances \
  -d '{"tenant_id":"demo","user":{"id":"skill-check"}}'
```

## Verification Goals

- confirm the target recipe is in `mode=app`
- confirm viewer bootstrap lists app recipes and a default recipe
- confirm the runtime payload is usable even when OpenUI parsing is unavailable
- confirm OpenUI is treated as presentation, while `ui_schema` remains the runtime source of truth
