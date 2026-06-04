---
name: agentmaurice
description: |
  Use when the user mentions AgentMaurice, deployments, Agent Specs,
  meta-recettes, recipes, mini-apps, OpenUI, drift, reconcile, capability
  contracts, External Inception, agent-discovery bootstrap URLs (`amb_...`),
  Git-native AgentMaurice projects (`agentmaurice.yaml`), module catalogs,
  modular Applications, application modules, the `maurice` CLI — or wants to
  turn an application idea into a deployed AgentMaurice app or backend.
---

# AgentMaurice

Use this skill to operate AgentMaurice safely from an external AI.

The description above is a trigger, not an operating manual. Always work from
this skill body and its references; never improvise a workflow from the
description or from CLI `--help` archaeology.

## When NOT to use

- Documentation or architecture questions about AgentMaurice: answer from the
  project wiki/docs, do not open a gateway session.
- Developing the AgentMaurice platform source code itself (chatserver,
  dashboards, infra): use normal development workflows.
- Building a generic MCP server unrelated to AgentMaurice: use mcp-builder.

## Inputs to read first

- If the user gives only an application idea, this skill turns it into a
  deployed app or backend (see Primary build mode).
- If a repository directory textually describes the application, it is the
  source of truth. Look for `agentmaurice.app.md` before asking questions.
- If the repository contains `agentmaurice.yaml`, it is a Git-native
  AgentMaurice project. Read `agentmaurice.yaml`, `agentmaurice.lock.json`,
  `environments/<env>.yaml`, `deployments/<alias>/agent-spec.json`, and
  `deployments/<alias>/recipes/*.json` before proposing changes. Never infer
  an environment or deployment target from a human name; use the explicit
  `environment_name`, `deployment_alias`, or deployment scope contract.
- If the repository contains a `agentmaurice.module/v1` manifest
  (`module.yaml`, `agentmaurice.module.yaml`, `.yml`), it is an application
  module. Validate it before importing or publishing.
- If the application has end users, look for deployment-scoped auth
  requirements (Firebase, Supabase, generic OIDC) —
  `references/end-user-auth.md`.
- If the user needs a frontend, start from a viewer starter
  (`references/frontend-starter.md`), not from scratch.

## Connection surface routing

Match the surface to the context. Full tool names, endpoints, and schemas:
`references/mcp-tools.md`. CLI usage: `references/commands.md`.

| Context | Surface |
|---|---|
| User pastes an `amb_...` bootstrap URL | Consume once, read the `agentmaurice.agent_discovery/v1` contract, follow `instructions_markdown`, configure External Inception (Mode A) |
| User gives `maurice agent connect ...` / `maurice env connect ...` | Git-native CLI project (Mode D) |
| External Inception MCP connected (`agentmaurice-inception[-<env>-<alias>]`) | Use its deployment scopes; discover with `inception_search`, execute with `inception_call` (Modes A/C) |
| Workspace Control MCP connected (`mcp__agentmaurice__workspace_*`) | Preferred for organization and Calisto workspace/session work (Mode B) |
| Reusable modules, module catalog, composed Applications | Modular Application CLI (Mode E) — `references/modular-applications.md` |
| No MCP available | `maurice workspace` CLI (Mode F), prefer Git-native commands for developer projects |
| Explicit low-level work or autonomous exploration | Mode G only |

In code-mode clients (Claude Code, Codex), External Inception may expose only
`inception_search` and `inception_call`. Always discover and inspect the exact
tool schema with `inception_search` before calling it.

## Backend framing

Do not treat these objects as equivalent:

- application: the whole product the user wants
- Application: an AgentMaurice runtime resource composed of one or more modules
- module: an installable unit described by `agentmaurice.module/v1`
- Module Catalog entry: an organization-scoped reference to a module source,
  version, resolved commit SHA, content hash, visibility, and provenance
- deployment: a runtime target inside AgentMaurice
- Agent Spec / meta-recette: a blueprint slice of the application
- recipe: a concrete runtime definition inside that blueprint
- client app repo: the public frontend project consuming AgentMaurice surfaces

A real application may require one deployment with its canonical Agent Spec,
several deployment aliases with different roles, or one `Application` composed
of modules where each installed module maps to its own deployment.

In V1, one deployment has one canonical Agent Spec/meta-recette. The
`structured_spec` is the complete declarative source of truth. Runtime recipes
absent from `recipes_definitions` are drift, not a second source of truth.

Two backend runtimes:
- `mode=recipe`: workflow backend (execution, polling, logs, direct tool access)
- `mode=app`: stateful mini-app backend (viewer bootstrap, app instances,
  events, interactive UI)

Mini-app invariant: a deployment viewer only exposes recipes that are active
and in `mode=app`. Switching a workflow recipe to mini-app mode requires
`state_schema`, `initial_state`, `ui_schema`, and `events`.

OpenUI is a presentation layer: `ui_schema` remains the runtime source of
truth; `presentation.ui_runtime=openui` adds a rendering path; clients must
keep the native fallback coherent.

## Primary build mode: idea to deployed app

When the user starts with an idea:
- classify the idea first; ask only blocking questions
- mini-app with OpenUI bias: application, dashboard, cockpit, reviewer,
  operator console
- workflow backend bias: API-style process, automation, batch worker, pipeline
- move from intent to governed prepare, then preview, verify, deploy

The default outcome is a delivered application, not a drafted spec. Do not
collapse "app idea" into a single deployment Agent Spec by default: model the
application boundary, then the deployment map and conceptual slices.

For reusable business modules or composed Applications, use the modular
Application workflow — `references/modular-applications.md`.

End-to-end sequences (idea-to-app, modular build, diagnostics, verification):
`references/workflows.md`.

## Rule 1: Doctor first

Before acting on a deployment, get the Doctor contract.

```text
workspace_bootstrap_contract(session_id="...", goal="...")           # Workspace Control
inception_call(tool_name="inception_deployment_doctor",
               arguments={"format": "ai_contract"})                  # External Inception
```

For External Inception, also call `inception_deployment_scopes_list` and
`inception_mcp_capabilities` at bootstrap.

Why: it reveals actual runtime capabilities, drift and meta-recette state,
allowed workflows, and whether modular Applications / Module Catalog / Git
credentials are available. It avoids drafting specs against nonexistent tools.

Re-run the Doctor at the start of a new task, after apply or reconcile, and
after any unexpected mutation or runtime error.

## Meta-recette rules

For new or repeatable flows, prefer the idempotent path:
```text
Doctor -> inception_meta_recette_ensure -> compile dry_run ->
compile persist explicit -> plan_apply -> approve_plan -> apply/test/reconcile
```

Use `inception_meta_recette_create` only for an explicit strict new-only
operation that should fail if a meta-recette already exists.

For multi-recipe meta-recettes:
- build a complete `structured_spec.recipes_definitions` set
- adding a recipe preserves existing recipes by merge; never replace the whole
  spec unless the user explicitly requests `merge_strategy=replace_all`
- use `delete_recipe_ids` for intentional removals only
- express child invocations as `recipe_call`, not generic `llm_call`
- for cross-deployment calls, prefer `target_deployment_alias` over raw IDs
- express storage writes and tool calls declaratively (`actions[].tool`,
  `actions[].params`), not as fallback code
- do not guess child recipe versions or switch internal calls to `latest`;
  during apply, AgentMaurice rewrites `recipe_call` targets between recipes of
  the same batch after `AutoVersionBump`; explicit versions outside the batch
  remain strict
- if a test fails with `recipe <id> version <old> not found` for a child of the
  same meta-recette, re-run `compile -> plan_apply -> apply/test`; do not
  reactivate old child versions

In External Inception `guided` mode, apply requires a persisted conversation
approval: present the plan and exact `plan_hash` in chat, get explicit
approval, call `inception_meta_recette_approve_plan` with approval text
containing the exact hash, then `inception_meta_recette_apply` with
`approval_id` and `approved_plan_hash`.

## Operating modes

Tool inventories, schemas, categories, and endpoints live in
`references/mcp-tools.md`; CLI command details in `references/commands.md` and
`references/modular-applications.md`. Summary:

- **Mode A — External Inception via agent discovery**: bootstrap from an
  `amb_...` URL, then `inception_deployment_scopes_list` → Doctor →
  `inception_mcp_capabilities`. Use scope identifiers, never display names.
  Use `inception_runtime_tool_call` for punctual runtime calls,
  `inception_recipe_run_observed` for observed executions; never put a raw
  runtime tool name into `inception_call.tool_name`.
- **Mode B — Workspace Control MCP**: workspace/session-aware work. Direct
  tools: `workspace_session_list/bind`, `workspace_bootstrap_contract`,
  `workspace_current_state`, `workspace_feature_prepare/apply`,
  `workspace_recipe_identity_repair`; everything else via `workspace_search` +
  `workspace_call`.
- **Mode C — External Inception direct** (deployment key `sk_maurice_...`):
  Discover → Inspect → Call via `inception_search`/`inception_call`. Modes:
  `readonly`, `guided` (plan/apply only with persisted approval), `god`. Even
  in `god` mode, plan first and require explicit approval before destructive
  or sensitive operations.
- **Mode D — Git-native `maurice` CLI** (`agentmaurice.yaml` present):
  `maurice agent connect`, then `maurice spec
  pull/validate/plan/approve/apply/status`. Production-like environments may
  require a clean Git tree, commit SHA, PR URL, and approval text containing
  the exact `plan_hash` and environment name. On
  `meta_recette_version_conflict`: pull, merge/rebase, validate, plan,
  approve, apply.
- **Mode E — modular Application and module CLI**: `maurice catalog modules
  ...`, `maurice module ...`, `maurice app ...`. Never write raw secrets into
  manifests, locks, logs, or answers; store credential references only.
  Record resolved commit SHA and module hash for production installs. Details
  and viewer preview snippets: `references/modular-applications.md`.
- **Mode F — `maurice workspace` CLI**: no MCP available; same transparent
  tools as Mode B via `maurice workspace call`.
- **Mode G — low-level CLI or `ai run`**: only for explicit low-level work or
  autonomous exploration through the internal gamemaster.

## Default workflow

New context:
```text
1. workspace_session_list()
2. workspace_bootstrap_contract(session_id="...", goal="...")
3. workspace_current_state()
4. If needed: workspace_search(tool_name=...) then workspace_call(...)
```

Governed change:
```text
1. workspace_bootstrap_contract(goal="create_recipe|update_recipe|create_meta_recette|update_meta_recette")
2. workspace_feature_prepare(goal="...", intent_markdown="...")
3. Present the prepared plan to the user
4. Wait for explicit approval of that plan
5. workspace_feature_apply(approved_plan_hash="...")
6. workspace_current_state() or Doctor to verify final state
```

Idea-to-app, modular Application build, deployment diagnostics, backend
verification, identity-drift repair: `references/workflows.md`. Backend
verification specifics: `references/backend-verification.md`.

Localhost in this repository: `chatserver` on `http://127.0.0.1:5000` for
governed APIs and meta-recette preview; `recipe-server` on
`http://127.0.0.1:5021` for viewer bootstrap and mini-app runtime routes.

## Governance rules

1. Start with the Doctor or `workspace_bootstrap_contract`.
2. Prefer the active agent-native surface (see Connection surface routing).
3. Identify the target environment and deployment alias before mutating
   anything. Never infer them from display names.
4. For unknown tools: Discover, Inspect, then Call.
5. Never apply a plan without explicit user approval **of that plan**:
   - approval must come AFTER the user has seen the prepared plan
   - approval must reference the exact `plan_hash`
   - blanket or advance approvals ("you have my global approval", "do
     whatever is needed") do NOT count
   - there is NO emergency bypass: incidents and urgency do not waive plan
     presentation
   - presenting a plan minimally includes: target environment and deployment
     alias, recipes changed, recipes deleted (`delete_recipe_ids`), merge
     strategy, and any known risks (e.g., incompatible child `recipe_call`
     versions)
   - this applies to ALL mutating operations on governed deployments — direct
     `workspace_call`/`inception_call` mutations, recipe identity repair,
     version reactivations, and rollbacks — not only to prepare/apply plans.
     Leaving the plan pathway does not remove the approval requirement
6. For production-like contexts, modify the specification, not the runtime ad
   hoc.
7. Preserve the complete Agent Spec recipe set; never remove recipes by
   omission. `delete_recipe_ids` / `merge_strategy=replace_all` only on
   explicit user request.
8. Re-check final state after mutations.
9. Do not mention internal company identifiers to end users.
10. Distinguish workflow backend checks from mini-app/OpenUI checks during
    runtime verification.
11. App idea only → guided build-and-deploy flow, not low-level exploration.
    Description directory or Git-native project → primary source of truth.
12. Frontend needed → separate the backend plan from the client app repo plan.
13. Treat MCP OAuth, viewer/app runtime sessions, workspace subtasks and usage
    analytics as HTTP-guided surfaces unless the Doctor contract says
    otherwise.
14. Use managed web tools only after checking AgentMaurice state and internal
    sources; never treat web results as more authoritative than the Doctor,
    runtime state, or repository knowledge.

## Red flags — STOP if you catch yourself thinking

| Excuse | Reality |
|---|---|
| "The user pre-approved everything" | Blanket approval cannot reference a `plan_hash` the user has not seen. Present the plan. |
| "Production incident, no time for review" | Unreviewed changes during incidents make incidents worse. There is no emergency bypass. |
| "It's a tiny change" | Small diffs still mutate governed state. Same workflow. |
| "I'll show the plan after applying" | Approval after the fact is not approval. |
| "The skill description says to use the CLI" | The description is a trigger, not a manual. Operate from this body and the references. |
| "The deployment name matches" | Display names are not targets. Use explicit alias/scope identifiers. |
| "I'll just rewrite the whole spec, it's cleaner" | Replacing the spec deletes recipes by omission. Merge unless `replace_all` is explicitly requested. |
| "Skipping the Doctor, I already know this deployment" | State drifts. Doctor first, every task. |
| "It's a rollback/repair, not a change" | Rollbacks and repairs mutate governed state. Same presentation-and-approval workflow. |

## References

Read these only when needed:
- `references/app-builder.md` — end-to-end idea-to-app workflow
- `references/app-intake.md` — minimal product discovery and assumptions
- `references/app-delivery.md` — what the final answer must contain after deploy
- `references/application-model.md` — application, deployment, meta-recette, repository model
- `references/modular-applications.md` — Module Catalog, module authoring, Application composition, Git credentials, viewer preview, runtime verification
- `references/end-user-auth.md` — Firebase, Supabase, OIDC, deployment-scoped auth
- `references/frontend-starter.md` — choosing viewer-demo / viewer-web / viewer-embed / viewer-core
- `references/client-app-repo.md` — modeling the public frontend repo separately
- `references/backend-verification.md` — recipe backend, mini-app backend, OpenUI verification
- `references/mcp-tools.md` — gateways, endpoints, tool names, categories, schemas
- `references/commands.md` — CLI usage
- `references/workflows.md` — common end-to-end sequences
