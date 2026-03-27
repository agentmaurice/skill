# From Idea to Workflow Backend

Use this when the user starts with a product idea that is better implemented as a backend workflow than as an interactive app.

## Prompt

```text
Use $agentmaurice to turn this idea into an AgentMaurice workflow backend.
Ask only blocking questions.
Prefer the governed recipe creation path.
Verify the backend surface after apply and tell me how it should be invoked.
Here is the idea:
"A backend that classifies incoming partner emails, extracts key fields,
and returns a readiness summary for downstream systems."
```

## Expected MCP Path

```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="create_recipe")
3. workspace_current_state()
4. workspace_feature_prepare(goal="create_recipe", intent_markdown="Build a backend that classifies incoming partner emails...")
5. Present the plan
6. workspace_feature_apply(approved_plan_hash="<hash>")
7. Verify the recipe backend surface
8. workspace_current_state()
```
