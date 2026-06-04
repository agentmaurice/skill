# AgentMaurice MCP — Current Gateway Reference

AgentMaurice exposes two external MCP gateways:
- Workspace Control: organization-scoped, workspace-aware, preferred when a
  Calisto workspace session is the active surface
- External Inception: deployment-scoped or explicitly multi-deployment-scoped
  control for code agents

AgentMaurice OS also exposes two code-agent connection paths:
- prompt-only agent discovery (`amb_...`) for users who do not install the CLI
- `maurice agent connect` (`amc_...`) for developers who want Git-native
  project files and local MCP client setup

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
- `workspace_capabilities_suggest_migration`

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
- `agentmaurice-inception` for prompt-only setup
- `agentmaurice-inception-<env>-<deployment-alias>` when configured by
  `maurice agent connect`

Endpoints:
- `POST <base_url>/api/v1/mcp/external/inception`
- `GET <base_url>/api/v1/mcp/external/inception`
- `DELETE <base_url>/api/v1/mcp/external/inception`
- legacy SSE: `GET <base_url>/api/v1/mcp/external/inception/sse`
- legacy SSE messages: `POST <base_url>/api/v1/mcp/external/inception/messages`

Auth:
- `Authorization: Bearer sk_maurice_...`
- This is a deployment API key. Do not use the organization `sk_maurice_orgctrl_...` key here.
- New keys may carry `external_inception_primary_deployment_id` and
  `external_inception_deployment_scopes`. Old keys without explicit scopes
  remain single-deployment on their first deployment edge.

Meta-tools:
- `inception_search`
- `inception_call`
- `inception_mcp_capabilities`
- `inception_deployment_scopes_list`

Use this gateway when you already have a deployment-scoped key, a consumed
agent-discovery contract, or an MCP client configured by `maurice agent
connect`.

In code-mode clients such as Claude Code and Codex, the gateway normally lists
only `inception_search` and `inception_call`. Always search first, inspect the
exact schema second, then call by exact name.

Initial calls:
```text
inception_call(tool_name="inception_deployment_scopes_list", arguments={})
inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
inception_call(tool_name="inception_mcp_capabilities", arguments={})
```

For modular Applications, inspect `modular_applications` in the Doctor
`ai_contract` and in `inception_mcp_capabilities`. It documents the Module
Catalog, schemas, CLI commands, management endpoints, generic runtime routes,
and security boundaries. In V1 these are documented HTTP/CLI surfaces, not
direct External Inception mutation tools.

When multiple deployment scopes are authorized, pass `deployment_alias`,
`deployment_id`, or `target_deployment_id` to tools that accept a target.
Never infer the target from display text. A forbidden target returns
`external_inception_deployment_scope_forbidden`.

Useful `inception_search` categories:
- `recipe`
- `deployment`
- `mcp`
- `dynamic_mcp`
- `registry`
- `skill`
- `function`
- `provider`
- `llm`
- `variable`
- `schedule`
- `meta_recette`
- `user`
- `access`
- `space`
- `rag`
- `allowlist`
- `multimodal`
- `integration`
- `storage`
- `messaging`
- `mailcatcher`
- `snapshot`
- `web`
- `devops`
- `observability`

## 3. Important expert tool families

### Meta-recette pipeline

Preferred high-level path:
- `workspace_feature_prepare`
- `workspace_feature_apply`

Low-level expert tools:
- `inception_meta_recette_list`
- `inception_meta_recette_get`
- `inception_meta_recette_ensure`
- `inception_meta_recette_create`
- `inception_meta_recette_update`
- `inception_meta_recette_compile`
- `inception_meta_recette_plan_apply`
- `inception_meta_recette_approve_plan`
- `inception_meta_recette_reject_plan`
- `inception_meta_recette_apply`
- `inception_meta_recette_test`
- `inception_meta_recette_reconcile`
- `inception_meta_recette_export`
- `inception_meta_recette_import`
- `inception_meta_recette_merge`
- `inception_meta_recette_project_export`
- `inception_meta_recette_project_validate`
- `inception_meta_recette_project_plan`
- `inception_meta_recette_project_apply`
- `inception_meta_recette_project_status`

Use `inception_meta_recette_ensure` for normal create-or-reuse workflows. Keep
`inception_meta_recette_create` for strict new-only flows where a duplicate
meta-recette must be treated as an error.

External Inception `guided` flow:
```text
1. inception_meta_recette_compile(dry_run=true, structured_spec={...})
2. inception_meta_recette_compile(dry_run=false, structured_spec={...})
3. inception_meta_recette_plan_apply(meta_recette_id="...")
4. Present the plan and exact plan_hash in the chat.
5. inception_meta_recette_approve_plan(
     meta_recette_id="...",
     plan_id="...",
     plan_hash="<hash>",
     approval_text="I approve <hash>"
   )
6. inception_meta_recette_apply(
     meta_recette_id="...",
     approval_id="...",
     approved_plan_hash="<hash>",
     run_tests=true
   )
```

`readonly` accepts compile only with `dry_run=true`. In `guided`, persistence
requires `dry_run=false` explicitly. The OS is an audit/supervision surface; it
is not required for approval when the user explicitly approves in chat.

Canonical Agent Spec rules:
- one canonical meta-recette/Agent Spec per deployment in V1
- `structured_spec.recipes_definitions` is the complete source of truth
- partial structured specs merge by default and preserve existing recipes
- removals must use `delete_recipe_ids`
- full replacement must use `merge_strategy="replace_all"`
- runtime recipes absent from the spec are drift; adopt them only with an
  explicit `adopt_runtime_orphans=true`

During apply, AgentMaurice computes final recipe versions first, including
`AutoVersionBump`, then rewrites internal `recipe_call` actions between recipes
generated in the same `recipes_definitions` batch. External explicit
`recipe_version` targets remain strict.

### Doctor and deployment inspection

- `inception_deployments_list`
- `inception_deployment_get`
- `inception_deployment_doctor`
- `inception_integrations_inventory`
- `inception_integrations_doctor`
- `inception_mcp_capabilities`

Doctor `ai_contract` also exposes modular Application metadata when supported:
- `capabilities.module_catalog`
- `capabilities.modular_applications`
- `capabilities.application_runtime`
- `capabilities.git_credentials`
- `modular_applications.schemas`
- `modular_applications.cli_commands`
- `modular_applications.catalog_endpoints`
- `modular_applications.application_management_endpoints`
- `modular_applications.runtime_endpoints`

Use this data to drive `maurice catalog modules`, `maurice module`,
`maurice app`, and `maurice git credential` commands. Do not invent direct
Inception module-mutation tools unless discovery explicitly lists them.

### Recipe definitions and executions

Low-level recipe management is based on recipe definitions:
- `inception_recipe_definitions_list`
- `inception_recipe_definitions_get`
- `inception_recipe_definitions_create`
- `inception_recipe_definitions_update`
- `inception_recipe_definitions_delete`
- `inception_recipe_definitions_activate`

Runtime and history flows:
- `inception_recipe_executions_start`
- `inception_recipe_executions_start_sync`
- `inception_recipe_executions_resume`
- `inception_recipe_executions_submit_form`
- `inception_recipe_executions_cancel`
- `inception_recipe_executions_approve`
- `inception_recipe_executions_list`
- `inception_recipe_executions_get`
- `inception_recipe_executions_logs`
- `inception_recipe_run_observed`
- `inception_recipe_execution_usage`

Deprecated compatibility helpers:
- `inception_recipe_executions_create`
- `inception_recipe_executions_update_status`

For user intent like "create an agent", prefer the meta-recette workflow, not raw recipe-definition CRUD.

Recipe runtime contract:
- `tool_call` actions use `actions[].tool` and `actions[].params`
- do not use `tool_name` or `inputs` in recipe action specs unless Doctor says
  a compatibility path is available
- prefer full runtime tool names such as `server--tool`; use short names only
  when non-ambiguous
- no-input recipes use `forms: []`
- form recipes follow `start -> waiting_for_form -> submit_form -> terminal`

Observed execution:
- `inception_recipe_run_observed` starts a recipe and returns result, data,
  logs, recipe trace, optional OTel trace, timeline, `trace_id`, and
  `usage_summary`
- `inception_recipe_execution_usage` returns only the execution cost/usage
  summary for comparison and optimization

### Backend verification surfaces

Use these when the user wants proof that AgentMaurice behaves like an external backend.

Workflow backend:
- recipe definitions via `inception_recipe_definitions_*`
- execution state via `inception_recipe_executions_get`
- external HTTP surface under `/recipe/<deploymentId>/...`

Mini-app backend:
- Doctor contract preview endpoints for `miniapp-preview`
- external HTTP surface under `/viewer/...` and `/app/...`

OpenUI delivery:
- discoverable through the Doctor AI contract
- expected when mini-app presentation uses `ui_runtime=openui`
- must keep a native fallback path

### MCP runtimes

- `inception_mcpservers_list`
- `inception_mcpsseservers_list`
- `inception_mcpsseservers_get`
- `inception_mcpsseservers_create`
- `inception_mcpsseservers_update`
- `inception_mcpsseservers_delete`
- `inception_mcpsseservers_doctor`
- `inception_mcpsseservers_redeploy`
- `inception_mcpstdioservers_list`
- `inception_mcpstdioservers_create`
- `inception_mcpstdioservers_delete`
- `inception_mcpsidecarservers_list`
- `inception_mcpsidecarservers_get`
- `inception_mcpsidecarservers_create`
- `inception_mcpsidecarservers_update`
- `inception_mcpsidecarservers_delete`
- `inception_mcpsidecarservers_redeploy`

### Dynamic MCP first-class control plane

Use these for managed/dynamic MCP instances, grants, grant policies, jobs and
audit. They are deployment-scoped and should be discovered through
`inception_search(category="dynamic_mcp", query="...")`.

- `inception_dynamic_mcp_instances_list`
- `inception_dynamic_mcp_instances_get`
- `inception_dynamic_mcp_instances_create`
- `inception_dynamic_mcp_instances_update`
- `inception_dynamic_mcp_instances_delete`
- `inception_dynamic_mcp_instances_redeploy`
- `inception_dynamic_mcp_grants_list`
- `inception_dynamic_mcp_grants_create`
- `inception_dynamic_mcp_grants_update`
- `inception_dynamic_mcp_grants_delete`
- `inception_dynamic_mcp_grant_policies_list`
- `inception_dynamic_mcp_grant_policies_create`
- `inception_dynamic_mcp_grant_policies_update`
- `inception_dynamic_mcp_grant_policies_delete`
- `inception_dynamic_mcp_jobs_list`
- `inception_dynamic_mcp_audit_list`

### Runtime MCP tools

Runtime tools, including `storage--*`, `memory--*`, `llm--*`,
`multimodal--*`, `docstore--*`, and `integration_*`, are visible through the
Doctor, capabilities, inventory, and resolve/list tools. They are not called by
placing their raw name in `inception_call.tool_name`.

Direct runtime tool entrypoint:
- `inception_runtime_tool_call`

Rules:
- `guided` can call visible deployment-scoped runtime tools directly
- `readonly` can resolve/dry-run but cannot execute direct runtime calls
- `god` has the same direct runtime tool ability as `guided`
- no arbitrary user ID can be supplied
- raw secrets are never returned

Example:
```text
inception_call(
  tool_name="inception_runtime_tool_call",
  arguments={
    "tool_name":"storage--list_files",
    "arguments":{},
    "timeout_sec":60
  }
)
```

If `inception_call(tool_name="storage--list_files")` returns a structured
blocked response, switch to `inception_runtime_tool_call`.

### Organization and deployment LLM control plane

Use these for organization providers, credential upsert/rotation, models,
profiles and deployment role config for `run`, `build` and `embedding`.

- `inception_org_llm_providers_list`
- `inception_org_llm_providers_get`
- `inception_org_llm_providers_create`
- `inception_org_llm_providers_update`
- `inception_org_llm_providers_delete`
- `inception_org_llm_credentials_upsert`
- `inception_org_llm_provider_test`
- `inception_org_llm_models_list`
- `inception_org_llm_models_create`
- `inception_org_llm_models_sync`
- `inception_org_llm_profiles_list`
- `inception_org_llm_profiles_create`
- `inception_org_llm_profiles_update`
- `inception_org_llm_profiles_delete`
- `inception_deployment_llm_config_get`
- `inception_deployment_llm_config_set`
- `inception_deployment_llm_config_select_model`

Never expect credential tools to return raw secret values. Treat credential
changes as sensitive mutations requiring an explicit plan and approval.

Hosted AgentMaurice LLM catalog:
- Doctor `allowed_llm_models` is the effective list of models callable by
  recipe `llm_call.llm_model`
- when the deployment uses AgentMaurice hosted, active `hosted:*` chat models
  from the Console catalog are callable explicitly, not only the run/build
  defaults
- inspect `llm_model_catalog` before choosing a model
- missing/unknown hosted model refs should be treated as stable config errors,
  not as prompts to expose provider secrets

### Registry, variables, providers, skills, schedules, spaces

- `inception_registry_stats`
- `inception_registry_deployment_status`
- `inception_registry_deployment_logs`
- `inception_registry_entry_tests`
- `inception_registry_check_image`
- `inception_variables_list`
- `inception_variables_get`
- `inception_llmproviders_list`
- `inception_llmproviders_get`
- `inception_embeddingproviders_list`
- `inception_embeddingproviders_get`
- `inception_skills_list`
- `inception_skill_registry_list`
- `inception_skill_registry_verify`
- `inception_schedules_list`
- `inception_spaces_list`

### Storage, snapshots, messaging, mail catcher, access

Use these to cover deployment configuration areas that are not recipes or MCP
runtimes.

Integrations are deployment-scoped at runtime:
- provider directory and billing are organization-level
- activation, settings, connections, runtime config, projected tools and usage
  are deployment-level
- a tool from another deployment must not appear callable unless it is enabled
  for the current deployment scope
- cross-deployment `recipe_call` runs the child recipe on the child deployment,
  using the child deployment's integrations

Integration discovery:
- `inception_integrations_inventory`
- `inception_integrations_doctor`

Snapshots:
- `inception_deployment_snapshot_export`
- `inception_deployment_snapshot_import`

S3 storage:
- `inception_s3_storage_get`
- `inception_s3_storage_create`
- `inception_s3_storage_update`
- `inception_s3_storage_delete`

Messaging accounts:
- `inception_messaging_accounts_list`
- `inception_messaging_accounts_get`
- `inception_messaging_accounts_create`
- `inception_messaging_accounts_update`
- `inception_messaging_accounts_delete`

Mail catcher routes:
- `inception_mailcatcher_routes_list`
- `inception_mailcatcher_routes_get`
- `inception_mailcatcher_routes_create`
- `inception_mailcatcher_routes_update`
- `inception_mailcatcher_routes_delete`

Deployment members:
- `inception_deployment_members_list`
- `inception_deployment_members_assign`
- `inception_deployment_members_remove`

Confirm before snapshot import, delete operations, credential changes,
membership changes, MCP removal, messaging account removal and mail route
removal.

### Managed websearch

Use these when AgentMaurice internal state and repository knowledge are not
enough, especially for external MCP documentation, third-party APIs, provider
errors and integration examples. Results must be cited by URL and must not
override Doctor/runtime truth.

- `inception_admin_web_search`
- `inception_admin_web_fetch`
- `inception_admin_web_extract`
- `inception_admin_web_mcp_docs`
- `inception_admin_web_github_readme`

The managed web gateway hides provider keys behind Console billing, quotas and
audit. Calisto and external MCP clients receive search/fetch/extract results,
not provider credentials.

### Runtime operations

- `inception_runtime_service_restart`

### Git-native project tools

Use these when the user works from a repository containing `agentmaurice.yaml`
or wants a multi-user workflow:

- `inception_meta_recette_project_export`
- `inception_meta_recette_project_validate`
- `inception_meta_recette_project_plan`
- `inception_meta_recette_project_apply`
- `inception_meta_recette_project_status`

Project format:
```text
agentmaurice.yaml
agentmaurice.lock.json
environments/<env>.yaml
deployments/<deployment-alias>/agent-spec.json
deployments/<deployment-alias>/recipes/<recipe_id>.json
deployments/<deployment-alias>/tests/test-plan.json
```

`project_plan` is non-mutating. `project_apply` requires `approval_id`,
`approved_plan_hash`, and matching `base_resource_version`. Version conflicts
return `meta_recette_version_conflict`.

## 4. Security and governance

External Workspace Control role header:
- `admin`: mutations allowed unless blocked by policy
- `operator`: runtime operations without broad admin mutation
- `readonly`: inspection only

External Inception mode:
- `readonly`: inspection, diagnostics, registry discovery/tests and dry-run
  validation
- `guided`: inspection, diagnostics, direct runtime tool calls, recipe
  execution, explicit compile persist, and governed apply with persisted
  conversation approval
- `god`: deployment-scoped mutations allowed unless explicitly blocked
- always blocked: API keys, sessions, organization memberships, auth connectors, raw secret reads, identity-sensitive user creation/deletion
- credential upserts may exist for specific admin control planes, but outputs must only expose status/presence metadata and never raw secret values

General rule:
- plan first
- show plan to the user
- persist conversation approval when in `guided`
- apply only after explicit approval
