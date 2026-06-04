# AgentMaurice Backend Verification

AgentMaurice can be treated as two backend runtimes:
- `mode=recipe`: workflow backend
- `mode=app`: mini-app backend

OpenUI belongs to the mini-app delivery path. It is not the runtime source of truth.

## 1. Recipe backend verification

Use this path when you need confidence that a deployment can execute workflow recipes for external consumers.

Recommended sequence:
1. List deployment scopes and choose the explicit alias or ID.
2. Get the Doctor contract.
3. Confirm the target recipe is active and in `mode=recipe`.
4. Execute the lightest useful observed runtime check.
5. Inspect execution status, logs, trace and `usage_summary` before concluding.

Preferred External Inception MCP path:
```text
inception_call(tool_name="inception_deployment_scopes_list", arguments={})
inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
inception_call(tool_name="inception_mcp_capabilities", arguments={"deployment_alias":"support"})
inception_call(tool_name="inception_recipe_run_observed", arguments={"deployment_alias":"support","recipe_id":"<recipe_id>","logs_limit":50,"trace_limit":50})
inception_call(tool_name="inception_recipe_execution_usage", arguments={"deployment_alias":"support","execution_id":"<execution_id>"})
```

Workspace Control can use the same Inception tools through `workspace_call`
when a Calisto workspace session is the active surface.

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
2. Confirm that the target recipe is active and in `mode=app`.
3. Verify viewer bootstrap or preview before deep runtime checks.
4. If needed, create an app instance and send one event.

Mini-app invariant:
- viewer bootstrap only lists active recipes in `mode=app`
- if a deployment contains only `mode=recipe` definitions, `GET /viewer/<deploymentId>` or `GET /viewer/s/<slug>` returns no mini-app for that deployment
- changing a recipe from `mode=recipe` to `mode=app` is not a one-field toggle: the definition must also provide `state_schema`, `initial_state`, `ui_schema`, and `events`

Runtime surface:
- `GET /viewer/<deploymentId>`
- `GET /viewer/s/<slug>`
- `POST /app/<deploymentId>/<recipeId>/instances`
- `GET /app/instances/<appInstanceId>`
- `POST /app/instances/<appInstanceId>/events/<eventId>`

Localhost runtime base in this repository:
- mini-app runtime via `recipe-server`: `http://127.0.0.1:5021`
- examples:
  - `http://127.0.0.1:5021/viewer/<deploymentId>`
  - `http://127.0.0.1:5021/viewer/s/<slug>`
  - `http://127.0.0.1:5021/app/<deploymentId>/<recipeId>/instances`

Build-time preview surface:
- `GET /organization/{organizationId}/meta-recette/{metaRecetteId}/miniapp-preview`
- `POST /organization/{organizationId}/meta-recette/{metaRecetteId}/miniapp-preview/events/{eventId}`

Localhost preview base in this repository:
- meta-recette preview via `chatserver`: `http://127.0.0.1:5000`

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
- recipe verification should include result, logs, traces and usage summary
- monetary billing is not invented locally; report estimated provider/runtime
  cost, credits or final monetary cost only when the runtime or billing source
  exposes them
