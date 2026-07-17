---
name: agentmaurice
description: >-
  Author, review, apply, and verify AgentMaurice Agent Specs with the Git-native
  `maurice` CLI. Use for AgentMaurice projects, Agent Spec V2, Agents,
  Workflows, MiniApps, Modules, managed-resource changes, drift diagnosis, or
  an AgentMaurice bootstrap command.
---

# AgentMaurice

Use the public Agent Spec V2 workflow. Keep the repository as the reviewed
source and let AgentMaurice compile it into runtime resources.

## Keep the object model exact

- **Agent Spec**: declarative desired state for one Agent.
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

Use this sequence for every managed change:

```text
connect -> init|pull -> edit -> commit -> spec deploy
        -> policy authorization or human gate -> apply -> verify
```

Do not mutate managed Workflows or MiniApps through direct administration
tools. Use an Agent Spec plan. Direct mutation is reserved for a sandbox that
the server explicitly reports as `unmanaged`.

### 1. Connect and inspect

Run a user-provided bootstrap command exactly as given:

```bash
maurice agent connect "<single-use-bootstrap-url>" \
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

`deploy` performs check, plan, apply, and verify. Sandbox, development, and
integration-test plans receive a traceable policy authorization and continue
without a human. When it returns exit code `4` with `awaiting_approval`, present
the Studio link and stop. Never approve with an agent/service credential.
After the authenticated human confirms the persisted plan, rerun the exact
same `spec deploy` command; it resumes that plan without asking the user for
IDs or hashes.

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
- a contract identifier or hash is incompatible;
- migration reports an ambiguous resource;
- a managed resource was changed out of band;
- the plan is stale or expired;
- human approval is absent or mismatched;
- a command requests a raw secret;
- verification detects drift, failed tests, or provenance mismatch.

Do not invent compatibility aliases, hidden mutations, or recovery commands.
