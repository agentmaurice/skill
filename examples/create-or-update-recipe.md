# Create or Update a Recipe

Use this when the user describes a business feature and wants the AI to turn it into an AgentMaurice recipe workflow.

## Prompt

```text
Use $agentmaurice to create or update a recipe for this feature:
"Create a support summary agent that classifies escalation level and writes a concise case summary."
Use the governed meta-recette workflow rather than low-level recipe-definition CRUD unless the exact definition layer is required.
Show me the plan before apply.
```

## Expected MCP Path

Create flow:

```text
1. workspace_bootstrap_contract(session_id="...", goal="create_recipe")
2. workspace_feature_prepare(goal="create_recipe", intent_markdown="Create a support summary agent that classifies escalation level and writes a concise case summary")
3. Present the plan
4. workspace_feature_apply(approved_plan_hash="<hash>")
```

Update flow:

```text
1. workspace_bootstrap_contract(session_id="...", goal="update_recipe")
2. workspace_feature_prepare(goal="update_recipe", intent_markdown="Add SLA risk scoring to the support summary agent")
3. Present the plan
4. workspace_feature_apply(approved_plan_hash="<hash>")
```

## Low-Level Alternative

Only use this if the user explicitly wants definition-level control:

```text
workspace_search(tool_name="inception_recipe_definitions_create")
workspace_call(tool_name="inception_recipe_definitions_create", arguments={...})
workspace_call(tool_name="inception_recipe_definitions_activate", arguments={"id":"...", "is_active":true})
```
