# Governed Meta-Recette Change

Use this when you want the AI to prepare a safe, reviewable Agent Spec change.

## Prompt

```text
Use $agentmaurice to prepare a governed update to the current AgentMaurice
Agent Spec. The requested change is: "Add spam detection to the support
workflow". Start with deployment scopes, Doctor and capabilities, prepare the
plan, show me the plan summary and exact plan_hash, ask for my explicit chat
approval, then apply only after that approval is persisted.
```

## Expected External Inception Path

```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract","deployment_alias":"support"})
3. inception_call(tool_name="inception_mcp_capabilities", arguments={"deployment_alias":"support"})
4. inception_call(tool_name="inception_meta_recette_ensure", arguments={"deployment_alias":"support","title":"Support Agent Spec"})
5. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":true,
     "structured_spec":{...}
   })
6. Verify merge_summary. Existing recipes must be preserved unless deletion or replace_all was explicitly requested.
7. inception_call(tool_name="inception_meta_recette_compile", arguments={
     "meta_recette_id":"mr_xxx",
     "dry_run":false,
     "structured_spec":{...}
   })
8. inception_call(tool_name="inception_meta_recette_plan_apply", arguments={"meta_recette_id":"mr_xxx"})
9. Present the plan and exact plan_hash to the user in chat.
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
12. inception_call(tool_name="inception_meta_recette_reconcile", arguments={"meta_recette_id":"mr_xxx"})
```

AgentMaurice OS is an audit and supervision surface for this path. It is not
required for approval when the user explicitly approves in the conversation.

## Expected Git-Native CLI Path

```bash
maurice spec pull --env dev --deployment-alias support
# edit deployments/support/agent-spec.json or deployments/support/recipes/*.json
maurice spec validate --env dev --deployment-alias support
maurice spec plan --env dev --deployment-alias support --out plan.json --json
maurice spec approve --env dev --plan plan.json --text "I approve dev <plan_hash>"
maurice spec apply --env dev --plan plan.json --approval-id <approval_id>
maurice spec status --env dev --deployment-alias support
```
