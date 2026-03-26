# AgentMaurice — Common Workflows

Each workflow starts with the preferred Workspace Control path, then a CLI fallback.

## 1. Deployment diagnostic

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

## 2. Governed meta-recette update

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

## 3. Create or update a recipe from user intent

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

## 4. Repair recipe identity drift

Use this when a previous buggy update created a rogue active recipe identity.

### Via Workspace Control MCP

```text
workspace_recipe_identity_repair(canonical_recipe_id="validation_recipe_x")
```

### Via CLI

```bash
maurice workspace call workspace_recipe_identity_repair --arg canonical_recipe_id=validation_recipe_x
```

## 5. Capability-contract inspection

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

## 6. Multi-deployment audit

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

## 7. Internal gamemaster exploration

Use `maurice ai run` when the user explicitly wants autonomous exploration or synthesis by the internal AgentMaurice model, not when you need a deterministic governed change pipeline.
