---
name: agentmaurice
description: |
  Control AgentMaurice via External Inception, Workspace Control MCP, or the
  `maurice` CLI. Trigger this skill whenever a user mentions AgentMaurice,
  agent-discovery bootstrap URLs, deployments, Agent Specs/meta-recettes,
  recipes, mini-apps, OpenUI, drift, reconcile, capability contracts,
  External Inception, Git-native AgentMaurice projects, module catalogs,
  modular Applications, application modules, application ideas, app builders,
  or the `maurice` CLI.
---

# AgentMaurice

<!-- BEGIN GENERATED OPERATING CONTRACT SUMMARY -->
## Operating Contract

This skill follows the shared AgentMaurice operating contract.

- Contract schema: agentmaurice.operating_contract/v1
- Contract version: 2026-06-10.1
- Contract hash: 2ea506e2899777ef2fd1be0447a070bf4ba989e34acea8811ca3ef7c96327986
- Canonical reference: references/operating-contract.md

Always apply the shared rules before mutating an AgentMaurice deployment: start with Doctor and capabilities, respect explicit scopes, keep Agent Specs as the source of truth, request approval for governed changes, and never expose raw secrets.
<!-- END GENERATED OPERATING CONTRACT SUMMARY -->

Use this skill to operate AgentMaurice safely from an external AI.

This skill should also be used when the user gives only an application idea and
wants the AI to turn it into a deployed AgentMaurice app or backend.

If the user already has a repository directory that textually describes the
application, read that directory first and treat it as the source of truth for
the build plan.

Look for a canonical file named `agentmaurice.app.md` before asking clarifying questions.

If the repository contains `agentmaurice.yaml`, treat it as a Git-native
AgentMaurice project. Read `agentmaurice.yaml`, `agentmaurice.lock.json`,
`environments/<env>.yaml`, `deployments/<deployment-alias>/agent-spec.json`,
and `deployments/<deployment-alias>/recipes/*.json` before proposing changes.
Never infer an environment or deployment target from a human name; use the
explicit `environment_name`, `deployment_alias`, or deployment scope contract.

If the repository contains `module.yaml`, `agentmaurice.module.yaml`,
`agentmaurice.module.yml`, or another declared `agentmaurice.module/v1`
manifest, treat it as an AgentMaurice application module. Validate the module
before importing or publishing it.

If the application has end users, look for deployment-scoped authentication requirements such as Firebase, Supabase, or generic OIDC.

If the user needs a client-facing or operator-facing frontend, prefer starting from a viewer starter such as `agent-maurice-viewer` instead of inventing a frontend from scratch.

Use the connection surface that matches the current context:

- If the user provides an `agent-discovery` bootstrap URL (`amb_...`), consume
  it once, read the returned `agentmaurice.agent_discovery/v1` contract, follow
  `instructions_markdown`, and configure/use External Inception if the client
  supports MCP setup.
- If the user provides a `maurice agent connect ...` or `maurice env connect ...`
  command, use the CLI path and the Git-native project it initializes.
- If an AgentMaurice External Inception MCP server is already connected, use it
  with the deployment scopes it exposes. The server may be named
  `agentmaurice-inception` for prompt-only setup, or
  `agentmaurice-inception-<env>-<deployment-alias>` when configured by
  `maurice agent connect`.
- If Workspace Control is connected, it remains the preferred organization and
  workspace-aware surface for Calisto workspace operations.

Workspace Control gives the AI:
- session binding to a Calisto workspace
- deployment targeting
- Doctor bootstrap
- governed prepare/apply workflows
- access to expert Inception tools through `workspace_search` and `workspace_call`

Use External Inception directly when a deployment-scoped key is available. In
code-mode clients such as Claude Code or Codex, External Inception may expose
only:
- `inception_search`
- `inception_call`

Always discover and inspect the exact tool schema with `inception_search`
before calling it with `inception_call`.

If MCP is not available, fall back to the `maurice` CLI. For a developer
project, prefer the Git-native commands `maurice agent connect`, `maurice env
connect`, `maurice spec ...`, `maurice catalog modules ...`,
`maurice module ...`, and `maurice app ...` over low-level ad hoc tool calls.

## Backend framing

Do not treat these objects as equivalent:
- application
- Application
- module
- Module Catalog entry
- deployment
- meta-recette
- recipe

Use this model:
- application: the whole product the user wants
- Application: an AgentMaurice runtime resource composed of one or more modules
- module: an installable unit described by `agentmaurice.module/v1`
- Module Catalog entry: an organization-scoped reference to a module source,
  version, resolved commit SHA, content hash, visibility, and provenance
- deployment: a runtime target inside AgentMaurice
- Agent Spec / meta-recette: a blueprint slice of the application
- recipe: a concrete runtime definition inside that blueprint
- client app repo: the public frontend project that consumes the AgentMaurice surfaces

A real application may require:
- one deployment with its canonical Agent Spec
- or several deployment aliases with different roles and Agent Specs
- or one AgentMaurice `Application` composed of modules, where each installed
  module maps to its own deployment

In V1, one deployment has one canonical Agent Spec/meta-recette. Treat the
`structured_spec` as the complete declarative source of truth for the recipes
visible and governed by AgentMaurice. Runtime recipes absent from
`recipes_definitions` are drift, not a second source of truth.

Treat AgentMaurice as two backend runtimes:
- `mode=recipe`: workflow backend for execution, polling, logs, and direct tool access
- `mode=app`: stateful mini-app backend for viewer bootstrap, app instances, events, and interactive UI

Important mini-app invariant:
- a deployment viewer only exposes recipes that are active and in `mode=app`
- if the deployment only contains `mode=recipe` definitions, viewer bootstrap returns no mini-app for that deployment
- switching a workflow recipe to mini-app mode requires app runtime fields such as `state_schema`, `initial_state`, `ui_schema`, and `events`

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

Do not collapse "app idea" into a single deployment Agent Spec by default.
Model the application boundary, then identify the deployment map and conceptual
slices.

If the user asks for reusable business modules, a catalog of modules, or an
Application composed from modules, use the modular Application workflow:
`maurice module validate/test` -> `maurice app init <dev-key> --kind test` ->
`maurice app add <dev-key> . --dev` -> preview with `agent-maurice-viewer` ->
publish/import -> `maurice app init <client-key> --kind standard` ->
`maurice app add` -> `maurice app plan` -> explicit approval ->
`maurice app apply --tests auto`.

## Rule 1: Doctor first

Before acting on a deployment, get the Doctor contract.

Preferred bootstrap:
```text
workspace_bootstrap_contract(session_id="...", goal="update_meta_recette")
```

External Inception bootstrap:
```text
inception_call(tool_name="inception_deployment_scopes_list", arguments={})
inception_call(tool_name="inception_deployment_doctor", arguments={"format": "ai_contract"})
inception_call(tool_name="inception_mcp_capabilities", arguments={})
```

Workspace expert path:
```text
workspace_call(tool_name="inception_deployment_doctor", arguments={"format": "ai_contract"})
```

Why:
- it reveals actual runtime capabilities
- it shows drift and current meta-recette state
- it tells the AI which workflows are allowed
- it tells the AI whether modular Applications, Module Catalog, Git
  credentials, and Application runtime routes are available
- it avoids drafting specs against nonexistent tools or providers

Re-run the Doctor:
- at the start of a new task
- after apply or reconcile
- after an unexpected mutation or runtime error

## Current meta-recette rules

For new or repeatable meta-recette flows, prefer the idempotent path:
```text
Doctor -> inception_meta_recette_ensure -> compile dry_run -> compile persist explicit -> plan_apply -> approve_plan -> apply/test/reconcile
```

Use `inception_meta_recette_create` only when the user explicitly wants a
strict new-only operation that should fail if a meta-recette already exists for
the target deployment.

For multi-recipe meta-recettes:
- build a complete `structured_spec.recipes_definitions` set
- when adding a recipe, preserve existing recipes by merge; do not replace the
  whole spec unless the user explicitly requests `merge_strategy=replace_all`
- use `delete_recipe_ids` for intentional removals
- express child invocations as `recipe_call`, not as generic `llm_call`
- for cross-deployment calls, prefer `target_deployment_alias` over raw IDs
- express storage writes as `tool_call` to the storage tool, not as fallback code
- express tool calls with `actions[].tool` and `actions[].params`
- do not guess child recipe versions or switch internal calls to `latest`
- during apply, AgentMaurice computes final recipe versions after
  `AutoVersionBump` and rewrites `recipe_call` targets between recipes generated
  in the same `recipes_definitions` batch
- explicit `recipe_version` values for recipes outside the current batch remain
  strict and must fail if the version does not exist

If a test fails with `recipe <id> version <old> not found` for a child generated
by the same meta-recette, run a new `compile -> plan_apply -> apply/test` cycle
so the parent recipe is rewritten. Do not reactivate old child versions as the
default fix.

In External Inception, every non-dry-run apply requires a persisted conversation
approval, including `god` mode. Present the plan and exact `plan_hash` to the
user in chat, ask for explicit approval, call
`inception_meta_recette_approve_plan` with approval text containing the exact
hash, then call `inception_meta_recette_apply` with `approval_id` and
`approved_plan_hash`. New approvals expire after 24 hours; expired or already
applied approvals must be recreated from a fresh plan. AgentMaurice OS is an
audit surface, not a required approval step.

## Preferred operating modes

### Mode A: External Inception via agent discovery

Use this when the user has pasted a bootstrap prompt from AgentMaurice OS or a
configured AgentMaurice External Inception MCP server is present.

Bootstrap prompt path:
```text
1. Call the `amb_...` bootstrap URL once.
2. Read the `agentmaurice.agent_discovery/v1` contract.
3. Follow `client_setup` if the MCP client can be configured.
4. Start with `inception_deployment_scopes_list`.
5. Call `inception_deployment_doctor(format="ai_contract")`.
6. Call `inception_mcp_capabilities`.
```

Use `deployment_alias`, `deployment_id`, or `target_deployment_id` from the
authorized scopes. Never infer the target from the deployment display name.

For runtime tools listed by Doctor or inventory:
- use `inception_runtime_tool_call` for direct punctual calls
- use `inception_recipe_run_observed` when the user wants to execute a recipe
  and see result, logs, trace, timeline, and `usage_summary`
- use `inception_recipe_execution_usage` to compare costs/tokens/duration
  across runs
- do not put a raw runtime tool name such as `storage--list_files` directly
  into `inception_call.tool_name`

### Mode B: Workspace Control MCP

Use this when the connector is present and the task is workspace/session aware.

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

### Mode C: External Inception MCP direct

Use this when an AgentMaurice External Inception connector is present, or when
the user provides an External Inception MCP configured with a deployment key
`sk_maurice_...`. With MauriceCLI, the connector is usually named
`agentmaurice-inception-<env>-<deployment-alias>`.

Default pattern:
```text
1. inception_call(tool_name="inception_deployment_scopes_list", arguments={})
2. inception_search(query="deployment doctor")
3. inception_search(tool_name="inception_deployment_doctor")
4. inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
5. inception_call(tool_name="inception_mcp_capabilities", arguments={})
6. inception_search(category="...", query="...")
7. inception_search(tool_name="exact_tool_name")
8. inception_call(tool_name="exact_tool_name", arguments={...})
```

Use these categories when looking for configuration tools:
- `dynamic_mcp` for first-class Dynamic MCP instances, grants, policies, jobs and audit
- `llm` for organization LLM providers, credentials, models, profiles and deployment role config
- `integration` for deployment-scoped integration inventory, doctor and runtime tools
- `storage` for S3 storage config
- `messaging` for messaging accounts
- `mailcatcher` for inbound mail routes
- `snapshot` for deployment import/export snapshots
- `access` for deployment members
- `web` for managed web search/fetch/extract when external documentation is needed

External Inception modes:
- `readonly` supports safe reads, diagnostics, discovery and dry-run validation
- `guided` supports reads, diagnostics, runtime tool calls, recipe execution,
  compile dry-run, explicit compile persist, and plan/apply only with persisted
  conversation approval
- `god` supports deployment-scoped mutations except always-blocked security boundaries; it never bypasses Agent Spec apply approval

Even in `god` mode, Agent Spec apply still requires a persisted `approval_id`
and matching `approved_plan_hash`. Plan first and require explicit approval
before destructive or sensitive operations such as delete, credential
upsert/rotation, snapshot import, deployment membership changes, MCP removal,
messaging removal or mail route removal.

### Mode D: Git-native `maurice` CLI

Use this when the repository has `agentmaurice.yaml`, or when the user has the
CLI and wants a reproducible team workflow.

Connection:
```bash
maurice agent connect "<cli-bootstrap-url>" --client claude-code --env dev --deployment-alias support --dir .
```

Supported V1 client values are `claude-code`, `codex`, `cursor`, `windsurf`
and `generic`. Use `generic` when the current client cannot be configured
automatically; it prints the MCP endpoint, bearer header and first prompt.

Project workflow:
```bash
maurice spec pull --env dev --deployment-alias support
maurice spec validate --env dev --deployment-alias support
maurice spec plan --env dev --deployment-alias support --out plan.json --json
maurice spec approve --env dev --plan plan.json --text "I approve dev <plan_hash>"
maurice spec apply --env dev --plan plan.json --approval-id <approval_id>
maurice spec status --env dev --deployment-alias support
```

Production-like environments may require a clean Git tree, commit SHA, PR URL,
and approval text containing both the exact `plan_hash` and environment name.
If apply returns `meta_recette_version_conflict`, export/pull again, merge or
rebase in Git, validate, plan, approve, and apply.

### Mode E: modular `Application` and module CLI

Use this when the user wants to build reusable modules, import public or private
Git modules, or compose an AgentMaurice `Application` from several modules.

Discovery:
```bash
maurice catalog modules list --json
maurice catalog modules search <query> --json
maurice catalog modules info <module_key> --json
```

Module authoring:
```bash
maurice module init booking --dir .
maurice module validate --file module.yaml
maurice module test --file module.yaml
maurice module publish
```

Local test Application:
```bash
maurice app init booking-dev --kind test --json
maurice app add booking-dev . --dev --json
maurice app add booking-dev users --json
maurice app plan booking-dev --out app-plan.json --json
maurice app apply booking-dev --plan app-plan.json --plan-hash <hash> --tests auto --json
maurice app docs booking-dev
```

Catalog import and sync:
```bash
maurice catalog modules import <url> --ref <branch-or-tag> --visibility organization --json
maurice catalog modules sync <entry_id> --json
```

Application composition:
```bash
maurice app init salon --kind standard --name "Salon Application" --json
maurice app add <application_id_or_key> <module_key> --json
maurice app add <application_id_or_key> <git-url> --ref <branch-or-tag> --json
maurice app plan <application_id_or_key> --out app-plan.json --json
maurice app apply <application_id_or_key> --plan app-plan.json --plan-hash <hash> --tests auto --json
maurice app status <application_id_or_key> --json
maurice app docs <application_id_or_key>
```

Viewer preview for a declared mini-app:
```tsx
<AgentMauriceViewer
  apiBaseUrl="https://api.example"
  apiKey="runtime_application_key"
  applicationKey="salon"
  moduleKey="booking"
  appKey="booking_widget"
  authAdapter={clientAuthAdapter}
/>
```

Web Component preview:
```html
<agent-maurice-viewer
  api-url="https://api.example"
  api-key="runtime_application_key"
  application-key="salon"
  module-key="booking"
  app-key="booking_widget"
  auth-token="end_user_bearer_token"
></agent-maurice-viewer>
```

Private Git:
```bash
maurice git credential create company-modules --provider github --auth-type https_token --secret-file .git-token
maurice git credential list --json
maurice git credential test <credential_id> --url <private-url> --json
maurice git credential revoke <credential_id>
```

Rules:
- never write raw Git tokens, SSH private keys, API keys, or bearer tokens into
  manifests, locks, logs, prompts, or final answers
- store only credential references
- do not install from a moving ref in production without recording the resolved
  commit SHA and module hash returned by the catalog/import plan
- `Application` kind is `standard` or `test`; `test` is a normal Application
  optimized for module development and default test execution
- `--tests auto` runs tests for `kind=test` and skips them for
  `kind=standard`; use `--tests on|off` only for an explicit override
- the viewer uses `X-API-Key` for the Application/runtime key and
  `Authorization: Bearer ...` for end-user auth
- `maurice app add . --dev` must run from a clean Git repo whose current
  commit is reachable from the configured remote
- `Application` management is CLI/HTTP in V1; External Inception discovers the
  surface but does not mutate it directly

### Mode F: `maurice workspace` CLI

Use this when MCP is not connected, or when a reproducible terminal workflow is better.

Preferred bootstrap:
```bash
maurice workspace auth issue --organization <org_id> --deployment <deployment_id>
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace tools list
```

Then use the prepared-plan lifecycle:
```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace plan prepare
maurice workspace plan inspect
maurice workspace plan approve --plan-hash <hash> --comment "I approve <hash>"
maurice workspace plan apply --run-tests=false
```

### Mode G: low-level CLI or `ai run`

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
   - Agent Specs and conceptual slices
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
8. Inspect the persisted prepared plan
9. Present the exact plan_hash to the user
10. workspace_session_approve_prepared_plan(plan_hash="...")
11. workspace_session_apply_prepared_plan(run_tests=false)
12. Verify runtime access and return the application map, access paths, backend surfaces, and next steps
```

For a modular Application build:
```text
1. Read the module or application brief.
2. Call Doctor and capabilities; confirm modular_applications is implemented.
3. If authoring modules, create or update each module manifest, validate it,
   and run module tests.
4. Create a test Application with `maurice app init <dev-key> --kind test`.
5. Add the local module with `maurice app add <dev-key> . --dev` and import
   dependencies from the Module Catalog when needed.
6. Apply with `--tests auto`, then preview declared mini-apps with
   `agent-maurice-viewer` using `applicationKey`, `moduleKey`, and `appKey`.
7. Publish or import each module into the Module Catalog, using Git credential
   refs for private repos.
8. Create or select the client AgentMaurice Application with
   `--kind standard`.
9. Add published modules, then run app plan.
10. Present the plan_hash, module hashes, resolved commit SHAs, and target
   deployments to the user.
11. Apply only after explicit approval.
12. Check app status and docs; verify at least one declared runtime capability.
```

For a governed change:
```text
1. workspace_bootstrap_contract(session_id="...", goal="create_recipe|update_recipe|create_meta_recette|update_meta_recette")
2. workspace_feature_prepare(goal="...", intent_markdown="...")
3. workspace_session_inspect_prepared_plan()
4. Present the exact plan_hash to the user
5. workspace_session_approve_prepared_plan(plan_hash="...")
6. workspace_session_apply_prepared_plan()
7. workspace_current_state() or Doctor again to verify final state
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

For localhost in this repository:
- use `chatserver` on `http://127.0.0.1:5000` for governed APIs and meta-recette preview
- use `recipe-server` on `http://127.0.0.1:5021` for viewer bootstrap and mini-app runtime routes

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
2. Prefer the active agent-native surface: agent-discovery/External Inception
   for deployment work, Git-native `maurice spec` for repository work, and
   Workspace Control for workspace/session work.
3. Identify the target environment and deployment alias before mutating anything.
4. For unknown tools, use Discover, Inspect, then Call.
5. Never apply a plan without explicit user approval.
6. Persist every Agent Spec apply approval with
   `inception_meta_recette_approve_plan`, including `god` mode; the approval
   text must contain the exact `plan_hash`.
7. For production-like contexts, modify the specification, not the runtime ad hoc.
8. Preserve the complete Agent Spec recipe set; do not remove recipes by
   omission.
9. Use `delete_recipe_ids` or `merge_strategy=replace_all` only when the user
   explicitly asks for deletion or full replacement.
10. For runtime tools, use `inception_runtime_tool_call` or a governed recipe
   execution, not a raw runtime tool name in `inception_call`.
11. Re-check final state after mutations.
12. Do not mention internal company identifiers to end users.
13. When the user asks for runtime verification, distinguish clearly between workflow backend checks and mini-app/OpenUI checks.
14. When the user provides only an app idea, optimize for a guided build-and-deploy flow rather than low-level platform exploration.
15. When the user provides an application description directory or a Git-native
    AgentMaurice project, treat it as the primary source of truth and map it to
    environments, deployment aliases, Agent Specs and conceptual slices.
16. When the user needs a frontend, separate the AgentMaurice backend plan from the client app repo plan.
17. When using External Inception, use `inception_search` and `inception_call`; do not assume raw tools are directly listed in code-mode clients.
18. Treat MCP OAuth, viewer/app runtime sessions, workspace subtasks and usage analytics as HTTP-guided surfaces unless the Doctor contract says otherwise.
19. Use managed web tools only after checking AgentMaurice state and internal sources; cite URLs and never treat web results as more authoritative than the Doctor, runtime state, or local repository knowledge.

## References

Read these only when needed:
- `references/app-builder.md` for the end-to-end idea-to-app workflow
- `references/app-intake.md` for minimal product discovery and assumptions
- `references/app-delivery.md` for what the final answer should contain after deploy
- `references/application-model.md` for the application, deployment, meta-recette, and repository model
- `references/modular-applications.md` for Module Catalog, module authoring,
  Application composition, Git credentials, and runtime verification
- `references/end-user-auth.md` for Firebase, Supabase, OIDC, and deployment-scoped auth connector guidance
- `references/frontend-starter.md` for choosing between `viewer-demo`, `viewer-web`, `viewer-embed`, and `viewer-core`
- `references/client-app-repo.md` for modeling the public frontend repo separately from the backend app manifest
- `references/backend-verification.md` for recipe backend, mini-app backend, and OpenUI verification
- `references/mcp-tools.md` for current gateway and tool names
- `references/commands.md` for CLI usage
- `references/workflows.md` for common end-to-end sequences
- `references/credential-hygiene.md` for credential scope, local storage, roles,
  approval identity, and secret handling
