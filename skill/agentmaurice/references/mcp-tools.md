# AgentMaurice MCP — Current Gateway Reference

AgentMaurice exposes two external MCP gateways:
- Workspace Control: organization-scoped, workspace-aware, preferred
- External Inception: deployment-scoped alternative

## 1. Workspace Control

Server:
- `agentmaurice-workspace-control`

Main endpoint:
- `POST <base_url>/api/v1/organization/<org_id>/mcp/external/workspace`
- `GET <base_url>/api/v1/organization/<org_id>/mcp/external/workspace`

Legacy compatibility endpoints:
- `GET <base_url>/api/v1/organization/<org_id>/mcp/external/workspace/sse`
- `POST <base_url>/api/v1/organization/<org_id>/mcp/external/workspace/messages`

Auth:
- `Authorization: Bearer sk_maurice_orgctrl_...`
- `X-AgentMaurice-Workspace-Role: admin|readonly|operator`

### Direct tools to prefer first

These are the most useful high-level entry points:
- `workspace_session_list`
- `workspace_session_bind`
- `workspace_bootstrap_contract`
- `workspace_current_state`
- `workspace_feature_prepare`
- `workspace_feature_apply`
- `workspace_recipe_identity_repair`
- `workspace_search`
- `workspace_call`

### Other important workspace tools

Reach these through `workspace_call` when needed:
- `workspace_session_get`
- `workspace_session_list_deployments`
- `workspace_session_set_target_deployment`
- `workspace_session_prepare_apply_plan`
- `workspace_session_inspect_prepared_plan`
- `workspace_session_approve_prepared_plan`
- `workspace_session_apply_prepared_plan`
- `workspace_session_reconcile`
- `workspace_session_clear_prepared_plan`
- `workspace_session_list_plan_approvals`
- `workspace_session_get_plan_approval`
- `workspace_capabilities_list_exports`
- `workspace_capabilities_list_imports`
- `workspace_capabilities_get_contract`
- `workspace_capabilities_search_registry`
- `workspace_capabilities_validate_imports`
- `workspace_capabilities_explain_breaking_changes`

### `workspace_search`

Use it to discover or inspect expert tools.

Arguments:
- `query`
- `category`
- `tool_name`

Categories commonly useful:
- `session_control`
- `inspect`
- `diagnostics`
- `tests`
- `spec_plan`
- `spec_apply`
- `runtime_mutation`
- `recipe`
- `meta_recette`
- `mcp`
- `provider`
- `variable`
- `schedule`
- `skill`
- `space`
- `rag`
- `devops`

### `workspace_call`

Execute a tool by exact name with JSON arguments.

Pattern:
```text
1. workspace_search(query="meta recette compile")
2. workspace_search(tool_name="inception_meta_recette_compile")
3. workspace_call(tool_name="inception_meta_recette_compile", arguments={...})
```

### Transparent tool contracts

`workspace_bootstrap_contract`
- optional `session_id` or `workspace_session_id`
- optional `goal`
- optional `target_deployment_id`
- returns bound context, Doctor contract, and recommended workflows

`workspace_current_state`
- optional `session_id` or `workspace_session_id`
- optional `target_deployment_id`
- optional `include_ai_contract`
- returns current workspace and target deployment state

`workspace_feature_prepare`
- required `goal`
- optional `intent_markdown`
- optional `title`
- optional `meta_recette_id`
- optional `recipe_id`
- optional `structured_spec`
- optional `additional_structured_spec`
- optional `implementation_priority`
- returns prepared plan data, often including a persisted plan and an `approved_plan_hash`

`workspace_feature_apply`
- optional `goal`
- optional `meta_recette_id`
- optional `approved_plan_hash` or `prepared_plan_hash`
- optional `run_tests`
- optional `fail_on_test_failure`
- optional `dry_run`

`workspace_recipe_identity_repair`
- required `canonical_recipe_id`
- optional `source_recipe_id`
- optional `meta_recette_id`

## 2. External Inception

Server:
- `agentmaurice-inception`

Endpoints:
- `POST <base_url>/mcp/external/inception`
- `GET <base_url>/mcp/external/inception/sse`

Auth:
- `Authorization: Bearer mk_...`

Meta-tools:
- `inception_search`
- `inception_call`

Use this gateway when you already have a deployment-scoped key and do not need workspace session management.

## 3. Important expert tool families

### Meta-recette pipeline

Preferred high-level path:
- `workspace_feature_prepare`
- `workspace_feature_apply`

Low-level expert tools:
- `inception_meta_recette_list`
- `inception_meta_recette_get`
- `inception_meta_recette_create`
- `inception_meta_recette_update`
- `inception_meta_recette_compile`
- `inception_meta_recette_plan_apply`
- `inception_meta_recette_apply`
- `inception_meta_recette_test`
- `inception_meta_recette_reconcile`
- `inception_meta_recette_export`
- `inception_meta_recette_import`
- `inception_meta_recette_merge`

### Doctor and deployment inspection

- `inception_deployments_list`
- `inception_deployment_get`
- `inception_deployment_doctor`

### Recipe definitions and executions

Low-level recipe management is based on recipe definitions:
- `inception_recipe_definitions_list`
- `inception_recipe_definitions_get`
- `inception_recipe_definitions_create`
- `inception_recipe_definitions_update`
- `inception_recipe_definitions_delete`
- `inception_recipe_definitions_activate`

Runtime and history flows:
- `inception_recipe_executions_list`

For user intent like "create an agent", prefer the meta-recette workflow, not raw recipe-definition CRUD.

### MCP runtimes

- `inception_mcpservers_list`
- `inception_mcpservers_get`
- `inception_mcpsseservers_redeploy`
- `inception_mcpsidecarservers_list`
- `inception_mcpsidecarservers_get`
- `inception_mcpsidecarservers_redeploy`

### Variables, providers, skills, schedules, spaces

- `inception_variables_list`
- `inception_variables_get`
- `inception_providers_list`
- `inception_skills_list`
- `inception_schedules_list`
- `inception_spaces_list`

### Runtime operations

- `inception_runtime_service_restart`

## 4. Security and governance

`admin`
- mutations allowed unless blocked by policy

`readonly`
- inspection only

General rule:
- plan first
- show plan to the user
- apply only after explicit approval
