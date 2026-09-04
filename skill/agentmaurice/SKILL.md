---
name: agentmaurice
description: >-
  Author, review, apply, and verify AgentMaurice Agent Specs with the Git-native
  `maurice` CLI. Use for AgentMaurice projects, Agent Spec V2, Agents,
  Workflows, MiniApps, Modules, managed-resource changes, drift diagnosis, or
  an AgentMaurice bootstrap command.
---

# AgentMaurice

Use the **unified org builder**: one session (External Inception MCP or Studio)
for architecture **and** Agent Spec. Repository is the reviewed source; typed
plans + human approval govern mutations.

## Keep the object model exact

- **Builder session**: org-capable credential exposes
  `inception_architecture_*` and `inception_agent_spec_*` together.
- **Architecture plan**: `agentmaurice.architecture.plan/v1` by default -
  Applications, members, surface, `llm.run_ref`, `mcp_grants`. The v2 schema
  is emitted only when the plan actually asks for `create_agent` or
  `created_ref`. Approve in OS; apply via MCP.
- **Agent Spec**: declarative desired state for one Agent.
- **Application**: product boundary (members + `public_surface` + Run config).
  Revue Application in OS Builder, not a separate Compose tool.
- **Agent**: deployed, operable product resource.
- **Workflow**: executable business process managed by an Agent Spec.
- **MiniApp**: interactive runtime surface managed by an Agent Spec.
- **Skill**: instructions loaded by a coding agent. A Skill is never a runtime
  action or deployable package.
- **Module**: versioned executable package that contributes Workflows,
  MiniApps, runtime schemas, assets, and documentation. Agent Specs and test
  plans stay in the consuming Agent project.

Never use `Skill` and `Module` interchangeably. Convert a package containing
executable resources into a Module; keep instruction-only content in the Skill
Catalog.

## Follow one authoring rail

Start with the org graph, then architecture and/or Agent Spec as needed:

```text
connect (org-builder) -> architecture observe
  -> architecture.plan (optional) -> human approve -> architecture apply -> verify
  -> agent_spec: connect -> init -> edit -> check -> commit -> plan
  -> human approval (separate principal) -> apply -> verify
```

CLI helpers: `maurice architecture observe|plan-get|approve|verify`,
`maurice app …`, `maurice spec …` (Application authoring and runtime:
[App delivery](references/app-delivery.md)).
`init` may be replaced by `pull` when remote desired state already exists.
Do not mutate managed Workflows or MiniApps via direct admin tools — use an
Agent Spec plan (except an explicit unmanaged sandbox).

### 1. Connect and inspect

Classify the connection surface before running anything:

| Input | Purpose | Required action |
|---|---|---|
| `amb_...` URL or `bootstrap_kind: external_inception_mcp` | External Inception MCP setup | Consume it only through the MCP client setup instructions. Never pass it to MauriceCLI. |
| `amc_...` URL or `bootstrap_kind: maurice_cli` | MauriceCLI project connection | Run the exact user- or OS-provided `maurice agent connect` command. |
| External Inception already configured | Existing MCP connection | Use the exposed Agent scopes and tools without reconnecting MauriceCLI. |

An error reporting the other bootstrap family is not evidence of an outdated
CLI. Never infer a client/server version mismatch from `wrong_bootstrap_kind`;
use the remediation returned by the command.

For a user- or OS-provided `amc_` bootstrap, run the command exactly as given:

```bash
maurice agent connect "https://instance.example/api/v2/agent-connections/cli-bootstrap/amc_xxx" \
  --client <claude-code|codex|cursor|windsurf|generic> \
  --env <environment> \
  --agent-alias <agent-alias> \
  --dir .
```

Never infer an organization, environment, Agent, or alias from a display name.
Use identifiers returned by the bootstrap or committed manifests.

The CLI may hold several AgentMaurice instances. Use the workspace-bound
context by default; inspect or switch explicitly when needed:

```bash
maurice context current --json
maurice context list
maurice context use <name>       # global default
maurice context bind <name>      # current project and managed MCP connection
```

Never conclude that a runtime MCP or tool is absent before calling
`inception_tools_list` or `maurice tools list`. `inception_mcp_capabilities`
describes the Agent Spec control plane, not the runtime inventory. A tool
reported as `workflow_only` is available but governed; it is not missing.

For an existing Agent, run the compact Studio Doctor before opening a thread
or preparing a plan:

```bash
maurice studio doctor --agent <agent-alias> --env <environment> --json
```

Confirm the canonical target, server/CLI/contract/Skill compatibility,
required Studio capabilities, governance, and blocking diagnostics. For an
agent or service principal, `can_approve` must remain `false`. Stop if a
blocking diagnostic covers `thread new`, `plan`, or `closeout`; use only the
redacted `next_actions[]` returned by the Doctor and never bypass it with a
direct HTTP call. Rerun the preflight after a context or version change.

For organization builders, use the organization Doctor before
`studio thread new --scope organization`. The org rail must verify
`builder_scope: organization`, a unique Chief, the v2 plan contract, and the
`create_agent`/`closeout` handoff path. If the Doctor returns
`organization_builder_scope_required`, the current session is Agent-scoped and
must not be bootstrapped as an organization session. Follow the redacted
`next_actions[]` exactly; do not invent aliases or internal identifiers in the
product output.

Before editing, read:

```text
agentmaurice.project.json
agentmaurice.lock.json
environments/<environment>.json
agents/<agent-alias>/agent-spec.json
agents/<agent-alias>/workflows/*.json
agents/<agent-alias>/miniapps/*.json
agents/<agent-alias>/tests/test-plan.json
```

If a V1 workspace is detected, every command except `spec migrate` stops with
`workspace_migration_required` and leaves the disk unchanged. Run `maurice
spec migrate --check`, then `spec migrate --write` only after a green preview.
Review the backup under `.git/agentmaurice/migrations/` and commit the
conversion before continuing. Do not hand-edit a partial migration.

## Choose the correct CLI rail

- Use `maurice studio` for a persisted conversation with Studio. The draft,
  revision, plan, and closeout live on the server-side thread.
- Use `maurice spec` for direct Git-native authoring from reviewed project
  files. Do not mix its provenance with a Studio plan.
- Use `maurice test studio` for a closed-loop test suite and structured
  verdict. Hermetic mode validates the CLI harness; live mode qualifies the
  real Studio/model path.

For Studio phase 2, keep one governed lifecycle:

```text
studio thread new -> studio say -> studio thread show --files --diff
  -> studio plan -> policy authorization or separate human approval
  -> studio closeout --wait -> apply(tests=auto) -> verify
```

`studio events --since <sequence> [--follow]` resumes after the last observed
sequence. `studio closeout --wait` resumes only the latest non-terminal plan
bound to that thread and revision; never copy or invent plan, hash, or approval
identifiers. Code `0` is success only after required tests and green verify.
If approval is absent, return `awaiting_approval` with code `4`, present the
Studio review link, and stop. After a separate authenticated human approves
the exact persisted plan, rerun the same closeout command.

For organization-scoped work, the thread new command targets the reserved
Chief internally, then hands off to the newly created Agent thread. If a
handoff or initialization step fails, keep any already committed
`created_applications` or `created_agents`, return `authoring_required`, and
wait for the human step instead of recreating the Agent or thread.

Use `studio new-cycle` after a verified change, `studio fork` to explore an
immutable revision without moving the source thread, and `studio thread
archive` to hide a completed thread without deleting the Agent. Use
`studio say --record` and `studio replay` only with
`$schema: agentmaurice.studio_dialogue/v1`; assert structured facts, never
model prose, credentials, signed URLs, or approval identifiers.

Interpret Studio exit codes consistently:

| Code | Meaning |
|---|---|
| `0` | completed; closeout tests and verification are green |
| `1` | terminal turn or plan failure |
| `2` | invalid arguments, dialogue script, or thread state |
| `3` | stale plan/revision or version conflict |
| `4` | server/auth unavailable or human approval awaited; inspect `error_code` |
| `5` | timeout; resume from `last_sequence` |

After a timeout or ambiguous response, read and reconcile server state before
retrying a mutation. Never run concurrent turns or closeouts on one thread.

### 2. Initialize explicitly

For a fresh Agent with no local or remote Agent Spec, run:

```bash
maurice spec init \
  --env <environment> \
  --agent-alias <agent-alias> \
  --title "<title>" \
  --dir . \
  --json
```

`spec init` creates authoring state only. It must not create runtime resources.
If remote state already exists, use `maurice spec pull` instead of overwriting
it. After a successful fresh `spec init`, do not run `spec pull`: the local
manifest and lock changes are expected and must be committed with the Agent
resource files.

### 3. Load the contract, then edit

Retrieve the embedded contract and a canonical example when the shape is not
already present locally:

```bash
maurice spec schema workflow --json
maurice spec example workflow --json
maurice spec schema miniapp --json
maurice spec explain contracts --json
```

Author one resource per file. Require `$schema`, `schema_version: 2`, and the
correct `kind`. Put Workflows under `workflows/` and MiniApps under `miniapps/`.
Use `workflow_call` for Workflow composition. Reference secrets by identifier;
never place secret values in manifests, locks, prompts, logs, or answers.

Workflow `llm_call` transport is runtime-managed. Do not add an uncontracted
`stream` field: configured OpenAI-compatible endpoints stream upstream and the
runtime reassembles the final text or JSON before downstream steps continue.
For direct LLM HTTP calls inside Deno `code_execution`, read
[Expert operations](references/expert-operations.md); those calls do not inherit
the native action transport.
Read the same reference before invoking a runtime tool from `code_execution`;
it defines the supported `callTool` import, signature, return value, context,
and native JSON templating pattern.

Treat `agent-spec.json` as intent and desired state. Do not embed discovered
runtime snapshots, generated editor state, or duplicate resource lists in it.

Read [Agent Spec V2 authoring](references/agent-spec-v2.md) for file boundaries,
ownership, dependencies, and MiniApp side-effect rules.
Read [Generated contract reference](references/generated/agent-spec-v2.generated.md)
only when an offline contract identifier or canonical example is needed. This
generated block is tied to the contract bundle hash in `skill-version.json`.

### 4. Check and commit

```bash
maurice spec check \
  --env <environment> \
  --agent-alias <agent-alias> \
  --dir . \
  --json

git diff --check
git status --short
git add <reviewed-files>
git commit -m "Describe the Agent Spec change"
```

Treat exit code `2` as an invalid contract. Repair from the diagnostic and run
`check` again. Do not plan an invalid or dirty workspace.

### 5. Deploy through the effective server policy

```bash
maurice spec deploy \
  --env <environment> \
  --agent-alias <agent-alias> \
  --tests auto \
  --dir . \
  --json
```

`deploy` performs check, plan, apply, and `maurice spec verify`. Sandbox, development, and
integration-test plans receive a traceable policy authorization and continue
without a human. When it returns exit code `4` with `awaiting_approval`, present
the Studio link and stop. Never approve on the user's behalf. Do not run `spec approve` with the code-agent credential. Never approve with an agent/service credential. After the authenticated human confirms the persisted plan, rerun the exact same `spec deploy` command; it resumes that plan without asking the user for IDs or hashes.

Review the semantic diff, risk, test policy, source commit, and environment.
Do not modify files after planning. Exit code `3` means stale state or a
version conflict: pull, merge or rebase, commit, then rerun `deploy`. A terminal
failed plan requires a new deploy. Success requires a green verification; the
CLI writes the lock only then.

## Use expert operations only when needed

Read [Expert operations](references/expert-operations.md) only for MCP-driven
diagnosis, schema retrieval, runtime observation, drift investigation, or an
explicit unmanaged sandbox task. Keep managed authoring on the CLI rail above.

Read [Modules](references/modules.md) only when packaging reusable executable
resources or migrating an old mixed Skill package.

For client delivery, load only the relevant reference:

- [Credential hygiene](references/credential-hygiene.md)
- [End-user authentication](references/end-user-auth.md)
- [Frontend starter](references/frontend-starter.md)
- [App delivery](references/app-delivery.md)

## Stop conditions

Stop and explain the exact boundary when:

- the target Agent or environment is ambiguous;
- Studio Doctor reports a blocking capability, compatibility, contract, or
  Skill diagnostic for the requested operation;
- a contract identifier or hash is incompatible;
- migration reports an ambiguous resource;
- a managed resource was changed out of band;
- the plan is stale or expired;
- human approval is absent or mismatched;
- a Studio plan is not the latest non-terminal plan for the exact thread and
  revision, or a mutation result cannot be reconciled after timeout;
- a command requests a raw secret;
- verification detects drift, failed tests, or provenance mismatch.

Do not invent compatibility aliases, hidden mutations, or recovery commands.
