---
name: agentmaurice
description: >-
  Author, review, apply, and verify AgentMaurice Agent Specs with the Git-native
  `maurice` CLI. Use for AgentMaurice projects, Agent Spec V2, Agents,
  Workflows, MiniApps, Modules, managed-resource changes, drift diagnosis, or
  an AgentMaurice bootstrap command.
---

# AgentMaurice

The local runtime is AgentMaurice One; thereafter call it Maurice. Use the
unified org builder: one External Inception MCP or Studio session for
architecture and Agent Spec. The repository is the reviewed source; typed plans
and a distinct human approval govern mutations.

## Keep the object model exact

- A builder session exposes `inception_architecture_*` and
  `inception_agent_spec_*` together.
- Architecture plans use `agentmaurice.architecture.plan/v1` by default
  (Applications, members, surface, `llm.run_ref`, `mcp_grants`); emit v2 only
  when creating an Agent (`create_agent`/`created_ref`). Approve in the OS and
  apply through MCP.
- Agent Spec is declarative desired state for one Agent. An Application is the
  product boundary (members, `public_surface`, Run config), reviewed in OS
  Builder. An Agent is deployed and operable; a Workflow is an executable
  business process; a MiniApp is an interactive runtime surface.
- A Skill is never a runtime action or deployable package. A Module is a
  versioned executable package contributing Workflows, MiniApps, runtime
  schemas, assets, and documentation. Agent Specs and test plans remain in the
  consuming Agent project. Keep instruction-only content in the Skill Catalog
  and do not use Skill and Module interchangeably.

## Follow one authoring rail

Start with the org graph, then use the needed rails:

```text
connect (org-builder) -> architecture observe
  -> architecture.plan (optional) -> human approve -> architecture apply -> verify
  -> agent_spec: connect -> init -> edit -> check -> commit -> plan
  -> human approval (separate principal) -> apply -> verify
```

Use `maurice architecture observe|plan-get|approve|verify`, `maurice app …`,
and `maurice spec …`; see [App delivery](references/app-delivery.md) for
Application/runtime details. `init` becomes `pull` when remote desired state
already exists. Managed Workflows and MiniApps are changed only through an
Agent Spec plan, except an explicitly unmanaged sandbox.

### Connect and inspect

Classify bootstrap input before running it:

| Input | Action |
|---|---|
| `amb_...` or `bootstrap_kind: external_inception_mcp` | Consume only through MCP client setup; never pass to MauriceCLI. |
| `amc_...` or `bootstrap_kind: maurice_cli` | Run the exact user/OS-provided `maurice agent connect` command. |
| Existing External Inception | Use its exposed Agent scopes/tools; do not reconnect MauriceCLI. |

`wrong_bootstrap_kind` is not evidence of a version mismatch; follow the
returned remediation. For an `amc_` URL, use:

```bash
maurice agent connect "https://instance.example/api/v2/agent-connections/cli-bootstrap/amc_xxx" --client <claude-code|codex|cursor|windsurf|generic> --env <environment> --agent-alias <agent-alias> --dir .
```

Never infer organization, environment, Agent, or alias from display names; use
bootstrap identifiers or committed manifests. Inspect the bound context with
`maurice context current --json`, `context list`, and, only when needed,
`context use <name>` or `context bind <name>`. Identify an existing Agent with
`maurice agent list --json`; use the guarded delete flow in
[Expert operations](references/expert-operations.md) for disposable Agents.

Do not conclude a runtime MCP/tool is absent before `inception_tools_list` or
`maurice tools list`; `inception_mcp_capabilities` is control-plane inventory,
and `workflow_only` means governed availability.

Before a Studio thread or plan, run Studio Doctor:
`maurice studio doctor … --json`. Organization builders run the organization
Doctor before `studio thread new --scope organization`; stop on blocking
diagnostics and follow only redacted `next_actions[]`. Require
`runner_identity_contract: agentmaurice.runner_identity/v1`; keep `actor`,
`requester`, and `scope` distinct. Stop on `identity_unproven`; never rebuild
identity from prompt text or command arguments. See [Expert operations](references/expert-operations.md).

Before editing, read the project, lock, environment, Agent Spec, workflows,
MiniApps, and test plan (`agentmaurice.project.json`,
`agentmaurice.lock.json`, `environments/<environment>.json`, and the matching
`agents/<agent-alias>/…` files). A V1 workspace permits only
`spec migrate`: run `spec migrate --check`, then `--write` only after a green
preview; review `.git/agentmaurice/migrations/`, commit the conversion, and
never hand-edit a partial migration.

## Choose the CLI rail

`maurice studio` persists Studio drafts/plans/closeout; `maurice spec` is
Git-native authoring and must not mix provenance with a Studio plan; `maurice
test studio` is the hermetic or live closed-loop harness. Lifecycle, exit
codes, organization handoff, dialogue replay, and Doctor preflight are in
[Expert operations](references/expert-operations.md). Never approve on the
user's behalf from a code-agent or service credential.

### Initialize, author, and check

For a fresh Agent:

```bash
maurice spec init --env <environment> --agent-alias <agent-alias> --title "<title>" --dir . --json
```

`spec init` creates authoring state only. If remote state exists, use
`maurice spec pull`; after fresh init, commit the local manifest/lock with the
resource files and do not pull.

When needed, retrieve schema/examples with `maurice spec schema workflow
--json`, `maurice spec example workflow --json`, `maurice spec schema miniapp
--json`, and `maurice spec explain contracts --json`. Author one resource per
file with `$schema`, `schema_version: 2`, the right `kind`, Workflows under
`workflows/`, MiniApps under `miniapps/`, and `workflow_call` for composition.
Reference secrets by identifier; never put secret values in manifests, locks,
prompts, logs, or answers. Read [Agent Spec V2 authoring](references/agent-spec-v2.md)
for boundaries and side effects, and the generated contract reference only for
offline identifiers; see `references/generated/agent-spec-v2.generated.md`,
tied to `skill-version.json`.

Treat `agent-spec.json` as intent and desired state: do not embed runtime
snapshots, generated editor state, or duplicate resource lists. Workflow
`llm_call` is runtime-managed (no uncontracted `stream`); Deno LLM HTTP or
`callTool` usage is documented in [Expert operations](references/expert-operations.md).

```bash
maurice spec check --env <environment> --agent-alias <agent-alias> --dir . --json
git diff --check
git status --short
git add <reviewed-files>
git commit -m "Describe the Agent Spec change"
```

Exit code 2 means an invalid contract: repair from diagnostics and check
again. Do not plan an invalid or dirty workspace.

### Plan, apply, and verify

```bash
maurice spec deploy --env <environment> --agent-alias <agent-alias> --tests auto --dir . --json
```

Deploy performs check, plan, apply, and `maurice spec verify`. Sandbox,
development, and integration-test plans may continue under policy authorization.
Exit 4 / `awaiting_approval` means present the Studio link and stop.
Never approve with an agent/service credential. Never approve on the user's behalf.
Do not run `spec approve` with the code-agent credential. After a distinct human confirms
the persisted plan, rerun the same deploy. Exit 3 requires pull, merge/rebase,
commit, and redeploy. Success is a green verify before the lock is written.

After a MiniApp deploy, `spec verify` and `maurice doctor` do not prove the page
works: follow the launch/debug loop in [App delivery](references/app-delivery.md)
from the Maurice home page. A missing control or failed action is a failed
delivery and requires a spec repair.

## Find models, connectors, and request secrets

Before writing `llm_model` or naming a service, query the live catalog; do not
guess or download one:

```bash
maurice catalog llm list
maurice catalog connector list --query "<service>"
```

Use the exact model `ref` (chat/decision) as `llm_model`. A catalog row means
the account is paired and that ref is allowed; Maurice calls it and the
Console wallet pays. Do not ask the home page to confirm the ref again. A
connector exposes a key/label and `api_key` or `connect`; `connect` is the
home-page button and `api_key`/`secret://` is a masked field. Never paste keys,
inspect another agent's secret store, or leave the person to type a key without
opening the masked page.

For each missing secret, use one request per `secret://` reference:

```bash
maurice action request --kind secret_input --resource <secret_ref> --constraint secret_ref=<secret_ref> --json
maurice viewer browser --human-action <action_id> --no-open
maurice action wait --id <action_id> --follow
```

Remove the `secret://` prefix when passing `secret_ref` to the request. The
viewer command starts in the background so it continues serving while waiting.
Navigate to the exact printed `http://127.0.0.1:<port>/#/human-action/<action_id>`
URL; `page_url` from the request does not collect the secret. Read Ressource:
if its label is wrong, load the newly printed full host/port/hash URL, never only
change the hash. Continue only on `stored` or `cancelled`; never type or resolve
the value. Read [Credential hygiene](references/credential-hygiene.md): tools
attach stored keys; never interpolate `secret://` in `code_execution`. On
`account_not_paired`, stop and ask for a key/local model or home-page pairing.
Do not read the hosted model endpoint, write `hosted:`, invent connector keys,
start a local model/server, buy credits, or create a provider.

If no model is named, ask the person to choose the home-page default. A personal
API key or local model is only used when requested; a local model must already
be answering. If credits are insufficient, report it and stop. Do not create a
provider or stand-in server. Airtable uses the same masked flow, then
`maurice tools call` for its listed tools; see [Modules](references/modules.md),
[MiniApp UI](references/miniapp-ui.md), [Credential hygiene](references/credential-hygiene.md),
[End-user authentication](references/end-user-auth.md),
[Frontend starter](references/frontend-starter.md), and [App delivery](references/app-delivery.md).

## Stop conditions

Stop on ambiguous Agent/environment, blocking Studio Doctor, incompatible
contract hash, ambiguous migration, managed drift, absent/mismatched approval,
stale Studio plan/thread revision, unreconciled mutation, any request to paste,
reveal, or invent a secret, or failed/drifting verification. Do not invent
aliases, hidden mutations, or recovery commands.
