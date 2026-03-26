# Governed Meta-Recette Change

Use this when you want the AI to prepare a safe, reviewable change.

## Prompt

```text
Use $agentmaurice to prepare a governed update to the current AgentMaurice
meta-recette. The requested change is: "Add spam detection to the support
workflow". Start with the Doctor, prepare the plan, show me the plan summary,
and wait for approval before apply.
```

## Expected MCP Path

```text
1. workspace_bootstrap_contract(session_id="...", goal="update_meta_recette")
2. workspace_feature_prepare(goal="update_meta_recette", intent_markdown="Add spam detection to the support workflow")
3. Present the plan
4. workspace_feature_apply(approved_plan_hash="<hash>")
5. workspace_current_state()
```

## Expected CLI Path

```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='Add spam detection to the support workflow'

# after approval
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```
