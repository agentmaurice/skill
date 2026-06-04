# Diagnose a Deployment

Use this when you want the AI to inspect an AgentMaurice deployment safely.

## Prompt

```text
Use $agentmaurice to diagnose this AgentMaurice deployment.
Start with deployment scopes, Doctor, capabilities and integration inventory.
Summarize the main issues, blocked surfaces, callable runtime tools, LLM model
catalog, recipe spec consistency, and recommended next actions.
Do not mutate anything.
```

## Expected External Inception Path

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. Choose the explicit deployment_alias or deployment_id from the returned scopes.
3. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
4. inception_call(tool_name="inception_mcp_capabilities", arguments={"deployment_alias":"support"})
5. inception_call(tool_name="inception_integrations_inventory", arguments={"deployment_alias":"support"})
6. inception_call(tool_name="inception_integrations_doctor", arguments={"deployment_alias":"support"})
7. If needed, inception_call(tool_name="inception_resolve_tools", arguments={"deployment_alias":"support","tool_name":"..."})
```

## Expected CLI Path

```bash
maurice spec status --env dev --deployment-alias support
maurice tools call inception_deployment_scopes_list --deployment <deployment_id>
maurice tools call inception_deployment_doctor --deployment <deployment_id> --arg format=ai_contract
maurice tools call inception_mcp_capabilities --deployment <deployment_id>
maurice tools call inception_integrations_inventory --deployment <deployment_id>
maurice tools call inception_integrations_doctor --deployment <deployment_id>
```

## What to Report

- deployment context and explicit alias/ID used
- Doctor health and `next_calls`
- `allowed_llm_models` and `llm_model_catalog`
- integration providers available in the directory vs enabled on this deployment
- visible runtime tools and whether direct call is supported
- recipe spec consistency, including runtime orphans
- blocked surfaces and the human action required
