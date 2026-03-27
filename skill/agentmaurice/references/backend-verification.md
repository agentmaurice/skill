# AgentMaurice Backend Verification

AgentMaurice can be treated as two backend runtimes:
- `mode=recipe`: workflow backend
- `mode=app`: mini-app backend

OpenUI belongs to the mini-app delivery path. It is not the runtime source of truth.

## 1. Recipe backend verification

Use this path when you need confidence that a deployment can execute workflow recipes for external consumers.

Recommended sequence:
1. Get the Doctor contract.
2. List recipe definitions and confirm the target recipe is active and in `mode=recipe`.
3. If possible, execute the lightest useful runtime check.
4. Inspect execution status, logs, and trace before concluding.

Preferred MCP path:
```text
workspace_bootstrap_contract(session_id="...")
workspace_current_state()
workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
workspace_call(tool_name="inception_recipe_definitions_get", arguments={"id":"<recipe_id>"})
workspace_call(tool_name="inception_recipe_executions_get", arguments={"id":"<execution_id>"})
```

External HTTP runtime surface:
- `GET /recipe/<deploymentId>/recipes`
- `POST /recipe/<deploymentId>/<recipeId>/start`
- `POST /recipe/<deploymentId>/<recipeId>/execute`
- `GET /recipe/status/<executionId>`
- `/recipe/<deploymentId>/tools/...`

## 2. Mini-app backend verification

Use this path when you need confidence that a deployment can expose interactive app-mode runtimes.

Recommended sequence:
1. Get the Doctor contract.
2. Confirm that the target recipe is in `mode=app`.
3. Verify viewer bootstrap or preview before deep runtime checks.
4. If needed, create an app instance and send one event.

Runtime surface:
- `GET /viewer/<deploymentId>`
- `GET /viewer/s/<slug>`
- `POST /app/<deploymentId>/<recipeId>/instances`
- `GET /app/instances/<appInstanceId>`
- `POST /app/instances/<appInstanceId>/events/<eventId>`

Build-time preview surface:
- `GET /organization/{organizationId}/meta-recette/{metaRecetteId}/miniapp-preview`
- `POST /organization/{organizationId}/meta-recette/{metaRecetteId}/miniapp-preview/events/{eventId}`

## 3. OpenUI verification

OpenUI verification is a mini-app verification variant, not a separate runtime.

What to check:
- `presentation.ui_runtime=openui` is present when OpenUI delivery is intended
- the viewer or runtime payload is still usable if OpenUI parsing is unavailable
- the native fallback remains coherent

Rules to remember:
- `ui_schema` remains the runtime source of truth
- OpenUI is optional presentation
- the safe fallback is the native UI tree

## 4. Practical conclusion

For the skill, the right user-facing framing is:
- AgentMaurice can be used as a governed configuration platform
- AgentMaurice can also be used as an external backend for workflows and mini-apps
- OpenUI strengthens the mini-app delivery story, but it does not replace the underlying mini-app runtime
