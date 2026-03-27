# AgentMaurice — Common Workflows

Each workflow starts with the preferred Workspace Control path, then a CLI fallback.

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
9. Present the plan
10. workspace_feature_apply(approved_plan_hash="<hash>")
11. workspace_current_state()
12. Return the application map, access details, and next steps
```

### Via CLI

```bash
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract --arg goal=create_meta_recette
maurice workspace call workspace_current_state
maurice workspace call workspace_feature_prepare --arg goal=create_meta_recette --arg intent_markdown='Build an operations cockpit for onboarding reviews'

# after approval
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
maurice workspace call workspace_current_state
```

## 2. Deployment diagnostic

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_search(query="deployment doctor")
4. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
5. workspace_call(tool_name="inception_mcpservers_list", arguments={})
6. workspace_call(tool_name="inception_variables_list", arguments={})
7. workspace_call(tool_name="inception_meta_recette_list", arguments={})
8. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
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

## 3. Governed meta-recette update

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...", goal="update_meta_recette")
2. workspace_feature_prepare(goal="update_meta_recette", intent_markdown="Add spam detection to support workflow")
3. Present the plan to the user
4. workspace_feature_apply(approved_plan_hash="<hash>")
5. workspace_current_state()
```

### Manual expert path

```text
1. workspace_call(tool_name="inception_meta_recette_list", arguments={})
2. workspace_call(tool_name="inception_meta_recette_get", arguments={"id":"mr_xxx"})
3. If needed, inspect the exact schema first with workspace_search(tool_name="inception_meta_recette_update")
4. workspace_call(tool_name="inception_meta_recette_update", arguments={"id":"mr_xxx", "content":"...", "structured_spec":{...}})
5. workspace_call(tool_name="inception_meta_recette_compile", arguments={"meta_recette_id":"mr_xxx"})
6. workspace_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
7. Present the plan to the user
8. workspace_call(tool_name="inception_meta_recette_apply", arguments={"meta_recette_id":"mr_xxx", "approved":true, "approved_plan_hash":"<hash>"})
9. workspace_call(tool_name="inception_meta_recette_reconcile", arguments={"meta_recette_id":"mr_xxx"})
```

### Via CLI

```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='Add spam detection to support workflow'

# after approval
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```

## 4. Create or update a recipe from user intent

Rule:
- prefer `workspace_feature_prepare`
- let the wrapper route recipe goals through the meta-recette workflow
- only use low-level `inception_recipe_definitions_*` when the user explicitly wants definition-level control

### Via Workspace Control MCP

Create flow:

```text
1. workspace_bootstrap_contract(session_id="...", goal="create_recipe")
2. workspace_feature_prepare(goal="create_recipe", intent_markdown="Create a support summary agent")
3. Present the plan to the user
4. workspace_feature_apply(approved_plan_hash="<hash>")
```

Update flow:

```text
1. workspace_bootstrap_contract(session_id="...", goal="update_recipe")
2. workspace_feature_prepare(goal="update_recipe", intent_markdown="Add escalation classification")
3. Present the plan
4. workspace_feature_apply(approved_plan_hash="<hash>")
```

### Low-level recipe-definition path

Use only for exact recipe-definition work:

```text
workspace_search(tool_name="inception_recipe_definitions_create")
workspace_call(tool_name="inception_recipe_definitions_create", arguments={...})
workspace_call(tool_name="inception_recipe_definitions_activate", arguments={"id":"...", "is_active":true})
```

### Via CLI

```bash
maurice workspace call workspace_bootstrap_contract --arg goal=create_recipe
maurice workspace call workspace_feature_prepare --arg goal=create_recipe --arg intent_markdown='Create a support summary agent'
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```

## 5. Verify a recipe backend

Use this when the user wants confidence that AgentMaurice can act as a workflow backend for external callers.

### Via Workspace Control MCP

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
4. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
5. workspace_call(tool_name="inception_recipe_definitions_get", arguments={"id":"recipe_x"})
6. If a run exists or is started, workspace_call(tool_name="inception_recipe_executions_get", arguments={"id":"exec_x"})
```

### Via CLI and backend endpoint

```bash
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract
maurice workspace call workspace_current_state
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_recipe_definitions_list --deployment <id>
maurice tools call inception_recipe_definitions_get --deployment <id> --arg id=recipe_x

# Optional direct runtime check
curl -X POST \
  -H "Authorization: Bearer <deployment_api_key>" \
  -H "Content-Type: application/json" \
  <base_url>/recipe/<deployment_id>/recipe_x/execute \
  -d '{"input":{}}'
```

## 6. Verify a mini-app and OpenUI backend

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

## 7. Repair recipe identity drift

Use this when a previous buggy update created a rogue active recipe identity.

### Via Workspace Control MCP

```text
workspace_recipe_identity_repair(canonical_recipe_id="validation_recipe_x")
```

### Via CLI

```bash
maurice workspace call workspace_recipe_identity_repair --arg canonical_recipe_id=validation_recipe_x
```

## 8. Capability-contract inspection

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

## 9. Multi-deployment audit

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

## 10. Internal gamemaster exploration

Use `maurice ai run` when the user explicitly wants autonomous exploration or synthesis by the internal AgentMaurice model, not when you need a deterministic governed change pipeline.
