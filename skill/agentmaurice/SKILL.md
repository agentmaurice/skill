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
connect -> init -> edit -> check -> commit -> plan
        -> human approval (separate principal) -> apply -> verify
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

If a V1 workspace is detected, run `maurice spec migrate --check`. The first
V2 `spec` command may perform the local migration, create a backup under
`.git/agentmaurice/migrations/`, and stop with
`workspace_migrated_commit_required`. Review and commit the conversion before
continuing. Do not hand-edit a partial migration.

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

### 5. Plan without changing runtime state

```bash
maurice spec plan \
  --env <environment> \
  --agent-alias <agent-alias> \
  --dir . \
  --json
```

Review the semantic diff, blast radius, risk, component versions, test policy,
source commit, and plan expiry. The default plan artifact stays outside the
worktree. Do not edit or reconstruct it.

### 6. Obtain human approval

Present the exact `plan_id`, `plan_hash`, target environment, destructive
actions, blast radius, and tests to the user. Ask for explicit approval.

Never approve on the user's behalf. Never treat a request to inspect, plan, or
prepare as approval. Stop after presenting the plan. An authenticated human
must approve it in AgentMaurice OS or run the following command from their own
human session:

```bash
maurice spec approve \
  --plan <plan-id-or-path> \
  --text "<verbatim-human-approval>" \
  --json
```

Do not run `spec approve` with the code-agent credential: agent and service
principals are rejected. Resume only after the persisted plan detail reports
`status: approved` and supplies the matching `approval_id`.

If approval is missing, expired, consumed, or does not match the exact plan
hash, stop and create a fresh approval for a fresh plan.

### 7. Apply the approved artifact exactly

```bash
maurice spec apply \
  --plan <plan-id-or-path> \
  --approval-id <approval-id> \
  --tests auto \
  --json
```

Do not modify files between plan and apply. Exit code `3` means stale state or
a version conflict: pull, merge or rebase, check, commit, plan, and request a
new approval. Never bypass the conflict.

Use `--tests off` only outside production, only when the user explicitly
authorizes it, and always provide the audited reason required by the CLI.

### 8. Verify desired and observed state

```bash
maurice spec verify --plan <plan-id-or-path> --wait --json
```

Require a match between desired state, runtime state, provenance, and blocking
tests. Report resource revisions and any drift. An apply or verification test
failure is a failure even if some resources were committed.

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
