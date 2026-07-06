# AgentMaurice — Common Workflows

Each workflow starts with the safest available agent-native surface. Use
External Inception when an agent-discovery contract or an AgentMaurice External
Inception MCP server is present, Workspace Control when a Calisto workspace is
bound, and Git-native `maurice spec` commands when the repository contains
`agentmaurice.yaml`.

Always choose environment and deployment target explicitly. Do not infer
`dev`, `preprod`, `prod`, or deployment aliases from display names.

## 1. Turn an idea into a deployed app

Use this when the user gives only a product idea and wants a real application outcome.

Rule:
- default to a mini-app with OpenUI when the idea sounds interactive
- ask only blocking questions
- preview and verify before apply
- model the application as deployments plus blueprint slices, not as a single artifact by default

### Via Workspace Control MCP

```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="create_meta_recette|create_recipe")
3. Read the application brief or description directory
4. workspace_current_state()
5. Model the application:
   - deployments
   - meta-recette slices
   - runtime mode for each slice
6. Choose the first slice:
   - interactive app slice -> create_meta_recette
   - workflow backend slice -> create_recipe or create_meta_recette
7. workspace_feature_prepare(goal="...", intent_markdown="...")
8. If mode=app, preview and verify the mini-app path
9. workspace_session_inspect_prepared_plan()
10. Present the exact plan_hash
11. workspace_session_approve_prepared_plan(plan_hash="<hash>")
12. workspace_session_apply_prepared_plan()
13. workspace_current_state()
14. Return the application map, access details, and next steps
```

### Via CLI

```bash
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract --arg goal=create_meta_recette
maurice workspace call workspace_current_state
maurice workspace call workspace_feature_prepare --arg goal=create_meta_recette --arg intent_markdown='Build an operations cockpit for onboarding reviews'
maurice workspace call workspace_session_inspect_prepared_plan
maurice workspace call workspace_session_approve_prepared_plan --arg plan_hash=<hash> --arg approval_comment='I approve <hash>'
maurice workspace call workspace_session_apply_prepared_plan --arg run_tests=false
maurice workspace call workspace_current_state
```

## 2. Deployment diagnostic

### Via External Inception MCP

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. Choose the explicit deployment_alias or deployment_id from the returned scopes.
3. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
4. inception_call(tool_name="inception_mcp_capabilities", arguments={"deployment_alias":"support"})
5. inception_call(tool_name="inception_integrations_inventory", arguments={"deployment_alias":"support"})
6. inception_call(tool_name="inception_integrations_doctor", arguments={"deployment_alias":"support"})
7. Summarize issues, blocked surfaces, available runtime tools, and next calls.
```

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_search(query="deployment doctor")
4. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
5. workspace_call(tool_name="inception_mcp_capabilities", arguments={})
6. workspace_call(tool_name="inception_integrations_inventory", arguments={})
7. workspace_call(tool_name="inception_mcpservers_list", arguments={})
8. workspace_call(tool_name="inception_variables_list", arguments={})
9. workspace_call(tool_name="inception_meta_recette_list", arguments={})
10. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
```

### Via CLI

```bash
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract
maurice workspace call workspace_current_state
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_mcpservers_list --deployment <id>
maurice tools call inception_variables_list --deployment <id>
maurice tools call inception_meta_recette_list --deployment <id>
maurice tools call inception_recipe_definitions_list --deployment <id>
```

### Runtime fix examples

```text
workspace_call(tool_name="inception_mcpsseservers_redeploy", arguments={"id":"srv_xxx"})
workspace_call(tool_name="inception_runtime_service_restart", arguments={"deployment_id":"dep_xxx", "operation":"restart"})
```

## 3. Compose a modular Application from modules

Use this when the user wants reusable modules or an AgentMaurice `Application`
composed of several modules.

### Via MauriceCLI

```bash
maurice whoami --json
maurice catalog modules list --json
maurice catalog modules search booking --json
maurice catalog modules info booking --json
```

For a private Git module:

```bash
maurice git credential create company-modules --provider github --auth-type https_token --secret-file .git-token
maurice git credential test <credential_id> --url <private-git-url> --json
maurice catalog modules import <private-git-url> --ref main --credential <credential_id> --visibility organization --json
```

For a module authored locally:

```bash
maurice module init booking --dir booking-module
cd booking-module
maurice module validate --file module.yaml
maurice module test --file module.yaml
maurice app init booking-dev --kind test --json
maurice app add booking-dev . --dev --json
maurice app plan booking-dev --out app-plan.json --json
maurice app apply booking-dev --plan app-plan.json --plan-hash <hash> --tests auto --json
maurice app docs booking-dev
maurice module publish --visibility organization --json
```

Use `agent-maurice-viewer` during this phase to preview declared mini-apps:

```tsx
<AgentMauriceViewer
  apiBaseUrl="https://api.example"
  apiKey="runtime_application_key"
  applicationKey="booking-dev"
  moduleKey="booking"
  appKey="booking_widget"
  authAdapter={clientAuthAdapter}
/>
```

Compose and apply:

```bash
maurice app init salon --kind standard --name "Salon Application" --json
maurice app add salon users --json
maurice app add salon booking --json
maurice app plan salon --out app-plan.json --json

# after explicit approval containing the plan_hash
maurice app apply salon --plan app-plan.json --plan-hash <hash> --tests auto --json
maurice app status salon --json
maurice app docs salon
```

Review before apply:
- exact `plan_hash`
- module key/version
- source URL, requested ref, resolved commit SHA and module hash
- target deployments and install/update/remove actions
- MCP and Agent Spec changes

Do not use raw secrets in manifests, overrides, logs or answers. Use only Git
credential references.

## 4. Governed meta-recette update

### Via External Inception governed apply

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
3. inception_call(tool_name="inception_meta_recette_ensure", arguments={"deployment_alias":"support","title":"Support Agent Spec"})
4. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":true,
     "structured_spec":{...}
   })
5. Check the merge_summary. Existing recipes must be preserved unless the user asked to delete or replace.
6. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":false,
     "structured_spec":{...}
   })
7. inception_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
8. Present the plan and exact plan_hash to the user in chat.
9. inception_call(tool_name="inception_meta_recette_approve_plan", arguments={
     "meta_recette_id":"mr_xxx",
     "plan_id":"plan_xxx",
     "plan_hash":"<hash>",
     "approval_text":"I approve <hash>"
   })
10. inception_call(tool_name="inception_meta_recette_apply", arguments={
      "meta_recette_id":"mr_xxx",
      "approval_id":"approval_xxx",
      "approved_plan_hash":"<hash>",
      "run_tests":true
    })
11. inception_call(tool_name="inception_meta_recette_test", arguments={"meta_recette_id":"mr_xxx"})
12. inception_call(tool_name="inception_meta_recette_reconcile", arguments={"meta_recette_id":"mr_xxx"})
```

The approval happens in the user/agent conversation and is persisted through
`inception_meta_recette_approve_plan`. This is required for every non-dry-run
apply, including `god` mode. AgentMaurice OS is only audit and supervision for
this path.

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...", goal="update_meta_recette")
2. workspace_feature_prepare(goal="update_meta_recette", intent_markdown="Add spam detection to support workflow")
3. workspace_session_inspect_prepared_plan()
4. Present the exact plan_hash to the user
5. workspace_session_approve_prepared_plan(plan_hash="<hash>")
6. workspace_session_apply_prepared_plan()
7. workspace_current_state()
```

### Manual expert path

```text
1. workspace_call(tool_name="inception_meta_recette_list", arguments={})
2. workspace_call(tool_name="inception_meta_recette_get", arguments={"id":"mr_xxx"})
3. Build a structured_spec patch that includes the new or updated recipes.
4. workspace_call(tool_name="inception_meta_recette_compile", arguments={"meta_recette_id":"mr_xxx","dry_run":true,"structured_spec":{...}})
5. Confirm merge_summary preserves existing recipes unless deletion/replacement was explicitly requested.
6. workspace_call(tool_name="inception_meta_recette_compile", arguments={"meta_recette_id":"mr_xxx","dry_run":false,"structured_spec":{...}})
7. workspace_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
8. Present the plan and exact plan_hash to the user.
9. Persist conversation approval. Non-dry-run apply always requires an approval_id.
10. workspace_call(tool_name="inception_meta_recette_apply", arguments={"meta_recette_id":"mr_xxx", "approval_id":"...", "approved_plan_hash":"<hash>","run_tests":true})
11. workspace_call(tool_name="inception_meta_recette_reconcile", arguments={"meta_recette_id":"mr_xxx"})
```

### Manual create-or-reuse path

Use this when Workspace Control is unavailable and the user wants a repeatable
create flow:

```text
1. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
2. workspace_call(tool_name="inception_meta_recette_ensure", arguments={"target_deployment_id":"dep_xxx","title":"...","content":"..."})
3. workspace_call(tool_name="inception_meta_recette_compile", arguments={"meta_recette_id":"mr_xxx","dry_run":true,"structured_spec":{...}})
4. workspace_call(tool_name="inception_meta_recette_compile", arguments={"meta_recette_id":"mr_xxx","dry_run":false,"structured_spec":{...}})
5. workspace_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
6. Present the plan and exact plan_hash to the user.
7. Persist explicit approval containing the plan_hash.
8. workspace_call(tool_name="inception_meta_recette_apply", arguments={"meta_recette_id":"mr_xxx","approval_id":"...","approved_plan_hash":"<hash>","run_tests":true})
```

Use `inception_meta_recette_create` only for strict new-only flows.

### Multi-recipe version mismatch recovery

If tests fail with `recipe <id> version <old> not found` for a child recipe
generated by the same meta-recette:

```text
1. Do not activate the old child version as the default fix.
2. Re-run inception_meta_recette_compile for the meta-recette.
3. Re-run inception_meta_recette_plan_apply.
4. After approval, re-run inception_meta_recette_apply with tests.
```

Apply realigns internal `recipe_call` versions to the final applied versions
after `AutoVersionBump`; explicit calls to recipes outside the current
`recipes_definitions` batch stay strict.

### Via CLI

```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='Add spam detection to support workflow'
maurice workspace call workspace_session_inspect_prepared_plan
maurice workspace call workspace_session_approve_prepared_plan --arg plan_hash=<hash> --arg approval_comment='I approve <hash>'
maurice workspace call workspace_session_apply_prepared_plan
```

## 5. Create or update a recipe from user intent

Rule:
- prefer External Inception guided or Git-native `maurice spec`
- use Workspace Control only when a workspace session is the active surface
- only use low-level `inception_recipe_definitions_*` when the user explicitly
  wants definition-level control
- when using `structured_spec`, include the new or updated recipe while
  preserving all existing `recipes_definitions`
- omission is not deletion; use `delete_recipe_ids` for explicit deletion
- use `merge_strategy:"replace_all"` only for an explicit complete replacement
- use `actions[].tool` and `actions[].params` for `tool_call`
- use `forms: []` for no-input recipes

### Via External Inception governed apply

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
3. inception_call(tool_name="inception_meta_recette_ensure", arguments={"deployment_alias":"support","title":"Support Agent Spec"})
4. Prepare structured_spec with the recipe to create or update.
5. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":true,
     "structured_spec":{...}
   })
6. Verify merge_summary.added/updated/preserved. Existing recipes must not disappear.
7. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":false,
     "structured_spec":{...}
   })
8. inception_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
9. Present the plan and exact plan_hash in chat.
10. inception_call(tool_name="inception_meta_recette_approve_plan", arguments={
      "meta_recette_id":"mr_xxx",
      "plan_id":"plan_xxx",
      "plan_hash":"<hash>",
      "approval_text":"I approve <hash>"
    })
11. inception_call(tool_name="inception_meta_recette_apply", arguments={
      "meta_recette_id":"mr_xxx",
      "approval_id":"approval_xxx",
      "approved_plan_hash":"<hash>",
      "run_tests":true
    })
12. inception_call(tool_name="inception_recipe_run_observed", arguments={"recipe_id":"recipe_x","logs_limit":50,"trace_limit":50})
```

### Via Git-native CLI

```bash
maurice spec pull --env dev --deployment-alias support
# edit deployments/support/recipes/<recipe_id>.json
maurice spec validate --env dev --deployment-alias support
maurice spec plan --env dev --deployment-alias support --out plan.json --json
maurice spec approve --env dev --plan plan.json --text "I approve dev <plan_hash>"
maurice spec apply --env dev --plan plan.json --approval-id <approval_id>
maurice spec status --env dev --deployment-alias support
```

### Via Workspace Control MCP

Create flow:

```text
1. workspace_bootstrap_contract(session_id="...", goal="create_recipe")
2. workspace_feature_prepare(goal="create_recipe", intent_markdown="Create a support summary agent")
3. workspace_session_inspect_prepared_plan()
4. Present the exact plan_hash to the user
5. workspace_session_approve_prepared_plan(plan_hash="<hash>")
6. workspace_session_apply_prepared_plan()
```

Update flow:

```text
1. workspace_bootstrap_contract(session_id="...", goal="update_recipe")
2. workspace_feature_prepare(goal="update_recipe", intent_markdown="Add escalation classification")
3. workspace_session_inspect_prepared_plan()
4. Present the exact plan_hash
5. workspace_session_approve_prepared_plan(plan_hash="<hash>")
6. workspace_session_apply_prepared_plan()
```

### Low-level recipe-definition path

Use only for exact recipe-definition work. This path can create runtime state
that is not represented in the canonical Agent Spec, so do not use it for
ordinary product changes.

```text
workspace_search(tool_name="inception_recipe_definitions_create")
workspace_call(tool_name="inception_recipe_definitions_create", arguments={...})
workspace_call(tool_name="inception_recipe_definitions_activate", arguments={"id":"...", "is_active":true})
```

## 6. Verify a recipe backend

Use this when the user wants confidence that AgentMaurice can act as a workflow backend for external callers.

### Via External Inception MCP

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
3. inception_call(tool_name="inception_mcp_capabilities", arguments={"deployment_alias":"support"})
4. inception_call(tool_name="inception_recipe_run_observed", arguments={
     "deployment_alias":"support",
     "recipe_id":"recipe_x",
     "logs_limit":50,
     "trace_limit":50
   })
5. inception_call(tool_name="inception_recipe_execution_usage", arguments={
     "deployment_alias":"support",
     "execution_id":"exec_x"
   })
6. Summarize status, result, trace_id, logs/traces, and usage_summary.
```

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
4. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
5. workspace_call(tool_name="inception_recipe_definitions_get", arguments={"id":"recipe_x"})
6. Start or inspect an observed run with workspace_call(tool_name="inception_recipe_run_observed", arguments={"recipe_id":"recipe_x","logs_limit":50,"trace_limit":50})
7. Compare usage with workspace_call(tool_name="inception_recipe_execution_usage", arguments={"execution_id":"exec_x"})
```

### Via CLI and backend endpoint

```bash
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_recipe_definitions_list --deployment <id>
maurice tools call inception_recipe_definitions_get --deployment <id> --arg id=recipe_x
maurice tools call inception_recipe_run_observed --deployment <id> --arg recipe_id=recipe_x --arg logs_limit=50 --arg trace_limit=50
maurice tools call inception_recipe_execution_usage --deployment <id> --arg execution_id=exec_x

# Optional direct runtime check
curl -X POST \
  -H "Authorization: Bearer <deployment_api_key>" \
  -H "Content-Type: application/json" \
  <base_url>/recipe/<deployment_id>/recipe_x/execute \
  -d '{"input":{}}'
```

## 7. Verify a mini-app and OpenUI backend

Use this when the user wants confidence that AgentMaurice can act as an interactive backend for external frontends.

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
4. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
5. Use the Doctor preview endpoints if a draft meta-recette is under review
6. Otherwise verify viewer bootstrap and, if needed, a live app instance
```

### Via CLI and backend endpoint

```bash
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract
maurice workspace call workspace_current_state
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_recipe_definitions_list --deployment <id>

# Viewer bootstrap
curl -H "Authorization: Bearer <deployment_api_key>" \
  <base_url>/viewer/<deployment_id>

# Optional live runtime check
curl -X POST \
  -H "Authorization: Bearer <deployment_api_key>" \
  -H "Content-Type: application/json" \
  <base_url>/app/<deployment_id>/<recipe_id>/instances \
  -d '{"tenant_id":"demo","user":{"id":"skill-check"}}'
```

OpenUI rule:
- keep the native fallback coherent even when OpenUI delivery is enabled

## 8. Repair recipe identity drift

Use this when a previous buggy update created a rogue active recipe identity.

### Via Workspace Control MCP

```text
workspace_recipe_identity_repair(canonical_recipe_id="validation_recipe_x")
```

### Via CLI

```bash
maurice workspace call workspace_recipe_identity_repair --arg canonical_recipe_id=validation_recipe_x
```

## 9. Capability-contract inspection

### Via Workspace Control MCP

```text
1. workspace_current_state()
2. workspace_call(tool_name="workspace_capabilities_list_exports", arguments={})
3. workspace_call(tool_name="workspace_capabilities_list_imports", arguments={})
4. workspace_call(tool_name="workspace_capabilities_validate_imports", arguments={})
```

### Via CLI

```bash
maurice workspace capabilities exports
maurice workspace capabilities imports
maurice workspace capabilities validate-imports
```

## 10. Multi-deployment audit

### Via Workspace Control MCP

```text
1. workspace_call(tool_name="inception_deployments_list", arguments={})
2. For each deployment, set target or bind a session
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"deployment_id":"dep_xxx","format":"json"})
```

### Via CLI

```bash
maurice tools call inception_deployments_list > /tmp/deps.json
for DEP in $(jq -r '.result[].id // .data[].id' /tmp/deps.json); do
  maurice tools call inception_deployment_doctor --deployment "$DEP" --arg format=json
done
```

## 11. Git-native AgentMaurice project workflow

Use this when a repository contains `agentmaurice.yaml` or the user wants team
collaboration through Git.

```bash
maurice spec pull --env dev --deployment-alias support
maurice spec validate --env dev --deployment-alias support
maurice spec plan --env dev --deployment-alias support --out plan.json --json
maurice spec approve --env dev --plan plan.json --text "I approve dev <plan_hash>"
maurice spec apply --env dev --plan plan.json --approval-id <approval_id>
maurice spec status --env dev --deployment-alias support
```

Rules:
- edit `deployments/<alias>/recipes/*.json`, not an incomplete replacement
  of the whole Agent Spec
- `recipes_definitions` is reconstructed from all recipe files
- keep `agentmaurice.lock.json` per environment and deployment alias
- use `target_deployment_alias` for cross-deployment `recipe_call` actions
- if apply returns `meta_recette_version_conflict`, pull/export again, merge
  in Git, validate, plan and apply again
- project apply is atomic across compile, runtime DB apply and approval
  consumption; if DB apply fails, compile changes are rolled back and the
  approval is released
- production-like environments can require clean Git, commit SHA, PR URL and
  approval text containing both the plan hash and environment name

## 12. Direct runtime MCP tool call

Use this for a punctual runtime MCP tool call without creating a recipe. Do not
put raw runtime tool names directly into `inception_call.tool_name`.

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_integrations_inventory", arguments={"deployment_alias":"support"})
3. inception_call(tool_name="inception_resolve_tools", arguments={"tool_name":"storage--list_files","deployment_alias":"support"})
4. inception_call(tool_name="inception_runtime_tool_call", arguments={
     "deployment_alias":"support",
     "tool_name":"storage--list_files",
     "arguments":{}
   })
```

Rules:
- `guided` can call visible runtime tools directly.
- `readonly` blocks direct execution outside supported dry-run/resolution.
- integration runtime tools are visible only when enabled for the target
  deployment.

## 13. Cross-deployment recipe call

Use this when one deployment is allowed to call a recipe in another explicitly
scoped deployment.

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. Choose aliases from the returned scopes, for example rh and users.
3. In the RH Agent Spec, use a recipe_call action:
   {
     "type":"recipe_call",
     "recipe_id":"users_find_by_email",
     "target_deployment_alias":"users",
     "input":{}
   }
4. Compile, plan, approve, apply, then run the RH recipe.
5. Verify the child execution is created on the users deployment and appears
   in traces/usage.
```

## 14. Connect a code agent to AgentMaurice

Prompt-only path for non-developers:

```text
1. User copies the AgentMaurice OS prompt containing an amb_... URL.
2. Call that URL once.
3. Read the agentmaurice.agent_discovery/v1 contract.
4. Configure MCP from client_setup if possible.
5. Start with scopes list, Doctor, and capabilities.
```

CLI path for developers:

```bash
maurice agent connect "<amc_bootstrap_url>" --client claude-code --env dev --deployment-alias support --dir .
```

Supported client values in V1:
- `claude-code`
- `codex`
- `cursor`
- `windsurf`
- `generic`

The CLI path initializes local credentials, writes non-secret project files,
pulls the Agent Spec, creates/consumes an External Inception bootstrap, and
configures the local MCP client when supported. The final `sk_maurice_...` key
must not be written into the project repository.

## 15. Internal gamemaster exploration

Use `maurice ai run` when the user explicitly wants autonomous exploration or synthesis by the internal AgentMaurice model, not when you need a deterministic governed change pipeline.
