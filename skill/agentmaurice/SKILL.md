---
name: agentmaurice
description: |
  Control AgentMaurice via the Workspace Control MCP gateway or the `maurice`
  CLI. Trigger this skill whenever a user mentions AgentMaurice, deployments,
  Calisto workspaces, meta-recettes, recipe definitions, mini-apps, OpenUI,
  drift, reconcile, capability contracts, External Inception, application
  ideas, app builders, or the `maurice` CLI.
---

# AgentMaurice

Use this skill to operate AgentMaurice safely from an external AI.

This skill should also be used when the user gives only an application idea and
wants the AI to turn it into a deployed AgentMaurice app or backend.

If the user already has a repository directory that textually describes the
application, read that directory first and treat it as the source of truth for
the build plan.

Look for a canonical file named `agentmaurice.app.md` before asking clarifying questions.

If the application has end users, look for deployment-scoped authentication requirements such as Firebase, Supabase, or generic OIDC.

If the user needs a client-facing or operator-facing frontend, prefer starting from a viewer starter such as `agent-maurice-viewer` instead of inventing a frontend from scratch.

Prefer the Workspace Control gateway when it is available. It gives the AI:
- session binding to a Calisto workspace
- deployment targeting
- Doctor bootstrap
- governed prepare/apply workflows
- access to expert Inception tools through `workspace_search` and `workspace_call`

If the MCP gateway is not available, fall back to the `maurice` CLI.

## Backend framing

Do not treat these objects as equivalent:
- application
- deployment
- meta-recette
- recipe

Use this model:
- application: the whole product the user wants
- deployment: a runtime target inside AgentMaurice
- meta-recette: a blueprint slice of the application
- recipe: a concrete runtime definition inside that blueprint
- client app repo: the public frontend project that consumes the AgentMaurice surfaces

A real application may require:
- one deployment with several meta-recettes
- or several deployments with different roles and different meta-recettes

Treat AgentMaurice as two backend runtimes:
- `mode=recipe`: workflow backend for execution, polling, logs, and direct tool access
- `mode=app`: stateful mini-app backend for viewer bootstrap, app instances, events, and interactive UI

Treat OpenUI as a presentation layer for mini-app delivery:
- `ui_schema` remains the runtime source of truth
- `presentation.ui_runtime=openui` adds an OpenUI rendering path
- clients must still keep the native fallback coherent

## Primary build mode: idea to deployed app

When the user starts with an idea rather than an existing recipe or meta-recette:
- classify the idea first
- ask only blocking questions
- prefer a mini-app with OpenUI when the user describes an application, dashboard, workspace, cockpit, reviewer, or operator console
- prefer a workflow backend when the user describes an API-style process, automation, batch worker, or pure backend pipeline
- move from intent to governed prepare, then preview, verify, and deploy

The default outcome should be a delivered application, not just a drafted spec.

Do not collapse "app idea" into "one meta-recette" by default.
Model the application boundary, then identify the deployment map and blueprint slices.

## Rule 1: Doctor first

Before acting on a deployment, get the Doctor contract.

Preferred bootstrap:
```text
workspace_bootstrap_contract(session_id="...", goal="update_meta_recette")
```

Manual expert path:
```text
workspace_call(tool_name="inception_deployment_doctor", arguments={"format": "ai_contract"})
```

Why:
- it reveals actual runtime capabilities
- it shows drift and current meta-recette state
- it tells the AI which workflows are allowed
- it avoids drafting specs against nonexistent tools or providers

Re-run the Doctor:
- at the start of a new task
- after apply or reconcile
- after an unexpected mutation or runtime error

## Preferred operating modes

### Mode A: Workspace Control MCP

Use this first when the connector is present.

Detection:
- `mcp__agentmaurice__workspace_search`
- `mcp__agentmaurice__workspace_call`

Key direct tools:
- `workspace_session_list`
- `workspace_session_bind`
- `workspace_bootstrap_contract`
- `workspace_current_state`
- `workspace_feature_prepare`
- `workspace_feature_apply`
- `workspace_recipe_identity_repair`

Expert access:
- `workspace_search`
- `workspace_call`

Important session tools are also reachable through expert mode, especially:
- `workspace_session_get`
- `workspace_session_list_deployments`
- `workspace_session_set_target_deployment`
- `workspace_session_prepare_apply_plan`
- `workspace_session_inspect_prepared_plan`
- `workspace_session_approve_prepared_plan`
- `workspace_session_apply_prepared_plan`
- `workspace_session_reconcile`
- `workspace_session_list_plan_approvals`

### Mode B: `maurice workspace` CLI

Use this when MCP is not connected, or when a reproducible terminal workflow is better.

Preferred bootstrap:
```bash
maurice workspace auth issue --organization <org_id>
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace tools list
```

Then call the same transparent tools as in MCP:
```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='...'
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```

### Mode C: low-level CLI or `ai run`

Use only when:
- the user explicitly wants low-level deployment tools
- workspace control is unavailable
- you need broad autonomous exploration through the internal gamemaster

## Default workflow

For a new context:
```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="...")
3. workspace_current_state()
4. If needed, use workspace_search with tool_name, then workspace_call
```

For an idea-to-app build:
```text
1. Read the idea or the application description directory
   - if `agentmaurice.app.md` exists, read it first
2. Model the application:
   - deployments
   - meta-recette blueprint slices
   - runtime surface per slice
   - end-user auth per deployment when applicable
   - frontend starter strategy when a public client app is needed
3. Classify each slice:
   - interactive app slice -> mode=app bias
   - backend workflow slice -> mode=recipe bias
4. Get the Doctor contract and current state for the target scope
5. Capture only the blocking product details
6. workspace_feature_prepare(goal="create_meta_recette|create_recipe", intent_markdown="...")
7. For mini-apps, preview and verify before apply
8. Present the plan to the user
9. workspace_feature_apply(approved_plan_hash="...")
10. Verify runtime access and return the application map, access paths, backend surfaces, and next steps
```

For a governed change:
```text
1. workspace_bootstrap_contract(session_id="...", goal="create_recipe|update_recipe|create_meta_recette|update_meta_recette")
2. workspace_feature_prepare(goal="...", intent_markdown="...")
3. Present the prepared plan to the user
4. workspace_feature_apply(approved_plan_hash="...")
5. workspace_current_state() or Doctor again to verify final state
```

For historical recipe identity drift:
```text
workspace_recipe_identity_repair(canonical_recipe_id="...")
```

For backend verification:
```text
1. workspace_bootstrap_contract(session_id="...")
2. workspace_current_state()
3. Choose the runtime:
   - recipe backend: inspect recipe definitions, then verify execution/state
   - mini-app backend: inspect viewer bootstrap, preview, or app-instance runtime
4. Prefer the lightest verification that proves the backend works
5. Do not apply a governed change unless the user explicitly switches from verification to mutation
```

## Tool naming rules

Recipe tools are centered on recipe definitions and executions.

Use names like:
- `inception_recipe_definitions_list`
- `inception_recipe_definitions_get`
- `inception_recipe_definitions_create`
- `inception_recipe_definitions_update`
- `inception_recipe_executions_list`

For business feature creation from user intent, prefer the meta-recette workflow over low-level recipe-definition CRUD.

## Governance rules

1. Start with the Doctor or with `workspace_bootstrap_contract`.
2. Prefer Workspace Control over low-level deployment-scoped access.
3. Identify the target deployment before mutating anything.
4. For unknown tools, use Discover, Inspect, then Call.
5. Never apply a plan without explicit user approval.
6. For production-like contexts, modify the specification, not the runtime ad hoc.
7. Re-check final state after mutations.
8. Do not mention internal company identifiers to end users.
9. When the user asks for runtime verification, distinguish clearly between workflow backend checks and mini-app/OpenUI checks.
10. When the user provides only an app idea, optimize for a guided build-and-deploy flow rather than low-level platform exploration.
11. When the user provides an application description directory, treat it as the primary source of truth and map it to deployments plus blueprint slices.
12. When the user needs a frontend, separate the AgentMaurice backend plan from the client app repo plan.

## References

Read these only when needed:
- `references/app-builder.md` for the end-to-end idea-to-app workflow
- `references/app-intake.md` for minimal product discovery and assumptions
- `references/app-delivery.md` for what the final answer should contain after deploy
- `references/application-model.md` for the application, deployment, meta-recette, and repository model
- `references/end-user-auth.md` for Firebase, Supabase, OIDC, and deployment-scoped auth connector guidance
- `references/frontend-starter.md` for choosing between `viewer-demo`, `viewer-web`, `viewer-embed`, and `viewer-core`
- `references/client-app-repo.md` for modeling the public frontend repo separately from the backend app manifest
- `references/backend-verification.md` for recipe backend, mini-app backend, and OpenUI verification
- `references/mcp-tools.md` for current gateway and tool names
- `references/commands.md` for CLI usage
- `references/workflows.md` for common end-to-end sequences
