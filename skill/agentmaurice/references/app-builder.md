# AgentMaurice App Builder

Use this reference when the user starts with an idea for an app, tool, cockpit, dashboard, portal, reviewer, assistant, or workflow product.

If the user provides a directory that describes the application, read that directory before deciding the build plan.

## 1. Classify the idea

Choose the runtime first.

Bias to `mode=app` when the user describes:
- a UI
- an operator console
- a dashboard
- a review surface
- a stateful workflow
- forms, events, or user actions

Bias to `mode=recipe` when the user describes:
- a background workflow
- an API-style backend
- a scheduled or triggered process
- a pure transformation pipeline
- no meaningful UI beyond logs or status

If the user says "application" and is vague, default to:
- `mode=app`
- `presentation.ui_runtime=openui`

But classify at the blueprint-slice level, not only at the whole-application level.
A single application may need both:
- `mode=app` slices
- `mode=recipe` slices

## 2. Build sequence

Preferred sequence:
1. Resolve the application model.
2. Identify deployments.
3. Identify meta-recette blueprint slices.
4. Identify end-user authentication requirements per deployment.
5. Get the Doctor contract.
6. Capture only blocking product details.
7. Prepare the governed change from user intent.
8. Preview and verify.
9. Apply after approval.
10. Re-check final state.
11. Return the deployment map, access details, and next steps.

When the application is large, build slice by slice instead of forcing one huge first apply.

## 3. Preferred MCP path

```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="create_meta_recette|create_recipe")
3. Read the application description directory or user brief
4. workspace_current_state()
5. Identify auth expectations for the deployment you are working on
6. Choose the deployment and blueprint slice you are working on
7. workspace_feature_prepare(goal="...", intent_markdown="...")
8. If mode=app, use preview or runtime verification
9. Present the plan
10. workspace_feature_apply(approved_plan_hash="...")
11. workspace_current_state()
```

## 4. Defaults

If the user does not specify these, assume:
- one primary user role
- one main view
- one main entity or result type
- one or two key actions
- safe verification before deployment

Do not assume:
- one deployment
- one meta-recette
- one runtime mode for the whole application

Avoid asking broad product-management questions if the app can be scaffolded from reasonable assumptions.
