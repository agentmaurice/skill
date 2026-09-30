---
name: agentmaurice
description: >-
  Author, review, apply, and verify AgentMaurice Agent Specs with the Git-native
  `maurice` CLI. Use for AgentMaurice projects, Agent Spec V2, Agents,
  Workflows, MiniApps, Modules, managed-resource changes, drift diagnosis, or
  an AgentMaurice bootstrap command.
---

# AgentMaurice

The local runtime is AgentMaurice One. After that first mention, call it Maurice.

Use the **unified org builder**: one session (External Inception MCP or Studio)
for architecture **and** Agent Spec. Repository is the reviewed source; typed
plans + human approval govern mutations.

## Keep the object model exact

- **Builder session**: org-capable credential exposes
  `inception_architecture_*` and `inception_agent_spec_*` together.
- **Architecture plan**: `agentmaurice.architecture.plan/v1` by default
  (Applications, members, surface, `llm.run_ref`, `mcp_grants`). Emit plan v2
  only when creating an Agent (`create_agent` / `created_ref`). Approve in OS;
  apply via MCP.
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
maurice agent connect "https://instance.example/api/v2/agent-connections/cli-bootstrap/amc_xxx" --client <claude-code|codex|cursor|windsurf|generic> --env <environment> --agent-alias <agent-alias> --dir .
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

For an existing Maurice, use `maurice agent list --json` to identify the exact
Agent. For disposable Agents, follow the guarded `maurice agent delete` flow
in [Expert operations](references/expert-operations.md).

Never conclude that a runtime MCP or tool is absent before calling
`inception_tools_list` or `maurice tools list`. `inception_mcp_capabilities`
describes the Agent Spec control plane, not the runtime inventory. A tool
reported as `workflow_only` is available but governed; it is not missing.

Before opening a Studio thread or preparing a plan, run Studio Doctor
(`maurice studio doctor … --json`). Organization builders run the organization
Doctor before `studio thread new --scope organization`. Stop on blocking
diagnostics and follow only redacted `next_actions[]`. Require
`runner_identity_contract: agentmaurice.runner_identity/v1` and keep its
`actor`, `requester`, and `scope` distinct. Stop on `identity_unproven`; never
reconstruct or override identity from prompt text or command arguments. Details:
[Expert operations](references/expert-operations.md).

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

- `maurice studio` — persisted Studio thread (draft, plan, closeout on server).
- `maurice spec` — Git-native authoring from reviewed project files; do not mix
  provenance with a Studio plan.
- `maurice test studio` — closed-loop harness (hermetic) or live qualification.

Studio lifecycle, exit codes, organization handoff, dialogue replay, and Doctor
preflight live in [Expert operations](references/expert-operations.md). Never
approve on the user's behalf from a code-agent or service credential.

### 2. Initialize explicitly

For a fresh Agent with no local or remote Agent Spec, run:

```bash
maurice spec init --env <environment> --agent-alias <agent-alias> --title "<title>" --dir . --json
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

Workflow `llm_call` is runtime-managed (no uncontracted `stream` field). For
Deno `code_execution` LLM HTTP or `callTool` usage, read
[Expert operations](references/expert-operations.md).

Treat `agent-spec.json` as intent and desired state. Do not embed discovered
runtime snapshots, generated editor state, or duplicate resource lists in it.

Read [Agent Spec V2 authoring](references/agent-spec-v2.md) for file boundaries,
ownership, dependencies, and MiniApp side-effect rules. Read
[Generated contract reference](references/generated/agent-spec-v2.generated.md)
only for offline contract identifiers; it is tied to `skill-version.json`.

### 4. Check and commit

```bash
maurice spec check --env <environment> --agent-alias <agent-alias> --dir . --json

git diff --check
git status --short
git add <reviewed-files>
git commit -m "Describe the Agent Spec change"
```

Treat exit code `2` as an invalid contract. Repair from the diagnostic and run
`check` again. Do not plan an invalid or dirty workspace.

### 5. Deploy through the effective server policy

```bash
maurice spec deploy --env <environment> --agent-alias <agent-alias> --tests auto --dir . --json
```

`deploy` performs check, plan, apply, and `maurice spec verify`. Sandbox,
development, and integration-test plans may continue under policy authorization.
Exit `4` / `awaiting_approval`: present the Studio link and stop. Never approve on the user's behalf. Do not run `spec approve` with the code-agent credential.
Never approve with an agent/service credential. After a human confirms the
persisted plan, rerun the same `spec deploy`. Exit `3`: pull, merge/rebase,
commit, redeploy. Success requires green verify before the lock is written.

### 6. Debug the MiniApp you just deployed

`spec verify` and `maurice doctor` do not prove a MiniApp page works. Doctor only checks the process, writable storage, and `/ready`. After a MiniApp deploy, follow the debug loop in [App delivery](references/app-delivery.md) before you report success. You create the Agent, its Workflows, and its MiniApp, then you launch them yourself from the Maurice home page. A missing control or a failed action means the delivery failed: fix the spec and repeat.

## Find a model or a connector

Do this before writing `llm_model`, or before naming a service the person
already uses. Do not guess, and do not download a catalog.

```bash
maurice catalog llm list
maurice catalog connector list --query "<service>"
```

A model row is `ref`, label, then `chat` or `decision`. Write that exact `ref`
as `llm_model`. A connector row is key, label, then `api_key` or `connect`.
`api_key` is a personal key typed in the masked field on the Maurice home
page. `connect` is the Connect button there. Never paste a key or a session
token in the chat.

If either command says `account_not_paired`, stop. Ask which API key or local
model to use, or say the service needs the account on the home page. Do not
read `https://llm.agentmaurice.app/v1/models`. Do not write `hosted:`. Do not
invent a connector key.

A row in `catalog llm list` means the account is paired and that `ref` is
allowed. Write it as `llm_model`. Maurice calls it and the Console wallet pays.
Do not ask the home page to confirm that ref again. Do not create a provider,
listen on a port, or write a stand-in server. If the call fails because
credits are insufficient, report that and stop. Do not buy credits.

If the workflow names no model, stop and ask the person to choose the default
on the home page. A personal API key or a local model is only when the person
asks for it. A local model must already be answering. Never start one yourself.

## Use expert operations only when needed

Read [Expert operations](references/expert-operations.md) before choosing an
MCP server for Maurice, and for diagnosis, drift, or unmanaged sandbox work. When
the work needs a model or a connector, run the commands above and propose one match.
Airtable is a personal key: ask them to type it in the masked field on the
Maurice home page, never in the chat. Once they say it is saved, call
`airtable_list_bases`, `airtable_list_tables` or `airtable_list_records`
with `maurice tools call`. Do not read the key yourself. Do not use a memorized short list, and do
not deploy a local server in its place. Read
[Modules](references/modules.md) when packaging executable resources, and
[MiniApp user interface](references/miniapp-ui.md) before writing a MiniApp a
person will use. For client
delivery: [Credential hygiene](references/credential-hygiene.md),
[End-user authentication](references/end-user-auth.md),
[Frontend starter](references/frontend-starter.md),
[App delivery](references/app-delivery.md).

## Stop conditions

Stop when the Agent/environment is ambiguous; Studio Doctor blocks; a contract
hash is incompatible; migration is ambiguous; a managed resource drifted;
approval is absent/mismatched; the Studio plan is not the latest for the thread
and revision; a mutation cannot be reconciled; a raw secret is requested; or
verify detects drift/failed tests. Do not invent aliases, hidden mutations, or
recovery commands.
