# From Idea to Mini-App

Use this when the user starts with a product idea and expects an interactive app.

## Prompt

```text
Use $agentmaurice to turn this idea into a deployed AgentMaurice mini-app.
Assume a mini-app with OpenUI unless the idea is clearly better as a workflow backend.
Ask only blocking questions.
Preview before apply.
Deploy it, verify it, then give me the app access path and next steps.
Here is the idea:
"A support lead dashboard that highlights urgent tickets, lets the lead review each case,
and trigger follow-up actions from the same app."
```

## Expected MCP Path

```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="create_meta_recette")
3. workspace_current_state()
4. workspace_feature_prepare(goal="create_meta_recette", intent_markdown="Build a support lead dashboard...")
5. Preview and verify the mini-app path
6. Present the plan
7. workspace_feature_apply(approved_plan_hash="<hash>")
8. workspace_current_state()
```
