# Create or Update a Recipe

Use this when the user describes a business feature and wants the AI to turn it
into an AgentMaurice recipe workflow.

## Prompt

```text
Use $agentmaurice to create or update a recipe for this feature:
"Create a support summary agent that classifies escalation level and writes a concise case summary."
Use the governed Agent Spec / Meta-Recette workflow rather than low-level
recipe-definition CRUD. Preserve all existing recipes in the spec. Show me the
plan and exact plan_hash before apply.
```

## Expected External Inception Path

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
3. inception_call(tool_name="inception_meta_recette_ensure", arguments={"deployment_alias":"support","title":"Support Agent Spec"})
4. Build structured_spec with the new or updated recipe.
   - Use actions[].tool and actions[].params for tool_call actions.
   - Use forms: [] when the recipe has no user input.
   - Use target_deployment_alias for cross-deployment recipe_call actions.
5. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":true,
     "structured_spec":{...}
   })
6. Confirm merge_summary.added/updated/preserved. Existing recipes must not disappear.
7. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":false,
     "structured_spec":{...}
   })
8. inception_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
9. Ask the user for explicit approval in chat and include the exact plan_hash.
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

## Expected Git-Native CLI Path

```bash
maurice spec pull --env dev --deployment-alias support
# create or edit deployments/support/recipes/<recipe_id>.json
maurice spec validate --env dev --deployment-alias support
maurice spec plan --env dev --deployment-alias support --out plan.json --json
maurice spec approve --env dev --plan plan.json --text "I approve dev <plan_hash>"
maurice spec apply --env dev --plan plan.json --approval-id <approval_id>
```

## Low-Level Alternative

Only use this if the user explicitly wants definition-level runtime control.
This path can create runtime state that is not represented in the canonical
Agent Spec, so it is not the normal product path.

```text
workspace_search(tool_name="inception_recipe_definitions_create")
workspace_call(tool_name="inception_recipe_definitions_create", arguments={...})
workspace_call(tool_name="inception_recipe_definitions_activate", arguments={"id":"...", "is_active":true})
```
