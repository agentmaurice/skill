# Diagnose a Deployment

Use this when you want the AI to inspect the current deployment safely.

## Prompt

```text
Use $agentmaurice to diagnose this AgentMaurice deployment.
Start with the Doctor contract, inspect MCP servers, variables, meta-recettes,
and recipe definitions, then summarize the main issues and recommended next actions.
Do not mutate anything.
```

## Expected MCP Path

```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. workspace_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
4. workspace_call(tool_name="inception_mcpservers_list", arguments={})
5. workspace_call(tool_name="inception_variables_list", arguments={})
6. workspace_call(tool_name="inception_meta_recette_list", arguments={})
7. workspace_call(tool_name="inception_recipe_definitions_list", arguments={})
```

## Expected CLI Path

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
