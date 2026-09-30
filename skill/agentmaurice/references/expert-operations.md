# Expert operations

## Resolve the instance and runtime inventory first

AgentMaurice contexts isolate instance URLs, credentials, organizations and
default Agents. Resolution order is `--context`, `MAURICE_CONTEXT`, the
workspace binding, then the global `current_context`. Start every diagnosis
with:

```bash
maurice context current --json
maurice tools list --json
maurice tools list --query "<needed capability>" --json
maurice tools describe <exact-tool-name> --json
maurice tools call <exact-tool-name> --dry-run --input-file ./tool-input.json --json
maurice tools call <exact-tool-name> --input-file ./tool-input.json \
  --idempotency-key "<stable-key>" --json
```

From External Inception, use the equivalent read-only tools directly:

1. `inception_tools_list` for the authoritative runtime inventory;
2. `inception_tools_resolve` for an intent or capability;
3. `inception_tools_describe` for the exact schema and invocation policy;
4. resolve the effective route with
   `inception_runtime_tool_call(dry_run=true)`;
5. execute with `inception_runtime_tool_call` and a stable
   `idempotency_key` only when `invocation.direct.allowed` is true;
6. direct calls are limited to `sandbox`, `development` and
   `integration_test`; staging and production always require a Workflow;
7. use `inception_workflow_executions_start_sync` or
   `inception_workflow_executions_start` for an applied Workflow, then inspect
   it with `inception_workflow_executions_get` and
   `inception_workflow_executions_logs`;
8. use `inception_agent_spec_workflow_preview` only for a valid sandbox draft;
9. otherwise declare the call in a managed Workflow when
   `invocation.workflow.allowed` is true;
10. report a missing capability only after an explicit `not_found` result.

Do not use `inception_mcp_capabilities` as proof that Memory, Brain, Docstore
or another runtime MCP is absent. Do not pass runtime tool names directly to
the generic `inception_call` wrapper.

Load this reference only for diagnosis, observation, schema discovery, drift,
or explicitly unmanaged sandbox administration. Managed authoring stays on the
Git-native CLI rail in `SKILL.md`.

## Identify and remove an Agent you own

Use `maurice agent list --json` to read exact IDs and names in the selected
organization. For a disposable Agent you created, first preview its dependent
MCP servers and deletion scope, then apply only when the ID and returned name
both match:

```bash
maurice agent delete --agent-id <id> --expect-name '<exact-name>' --json
maurice agent delete --agent-id <id> --expect-name '<exact-name>' --apply --json
```

Preview is read-only. Apply stops the Agent, removes its STDIO and sidecar MCP
servers, deletes the Agent and verifies its absence. It refuses reserved
instance Agents. Applications are independent and remain in place; use the
Application lifecycle for any disposable Application you also created. Never
delete an Agent inferred only from a display name, and never use this command
to clean another person's resources.

The local runtime is AgentMaurice One. After that first mention, call it Maurice.

## Choose an MCP server on Maurice

The person does not name servers. You choose. Start from `maurice tools list`.
Use a tool that is already running in Maurice when it does the job.

Maurice starts the MCP servers it needs. Do not start one beside it. Internal
servers, including Storage, already run inside the Maurice process. A file the
Workflow must read goes through that Storage MCP, not through a filesystem
server on the side.

**AgentMaurice Edge is only the bridge to a remote instance.** `maurice edge`
lends MCP servers that stay on this computer to a distant AgentMaurice (a
remote Maurice or a hosted instance). The remote instance decides the calls; Edge
only executes them. Do not use Edge when the runtime is the local Maurice. Edge
never starts Maurice, and it is not how Maurice gains a server.

**Which server.** Match the person's words to one row. A Storage file is not
a substitute. A Workflow `question` is not a substitute for `guard` or
`decision`. Your own notes, `MEMORY.md`, and this conversation are not a
substitute either: if the person wants something remembered, hidden, compared,
kept, explained, opened, read from a picture, or reached on a machine, call
the server in the table and show its result. Answering from this chat does
not count.

| The person wants | Server | Prove it with |
| --- | --- | --- |
| remember, recall, a fact, a preference, an appointment | `memory` | `memory.facts.append`, then `memory.query` on `v_facts_enriched` |
| hide or detect a secret, an email, a card, a password | `guard` | `guard_scan_v1`, then `guard_redact_v1` |
| a table, a CSV, which row is the largest | `data` | `data_profile_v1` or `data_query_v1` |
| a document they can keep | `artifact` | `artifact_create_v1` |
| why a run failed or which step was slow | `observe` | `observe_explain_v1` |
| call an API the organization already described | `api` | `api_health_v1`, then `api_call_v1` only for a known operation |
| find something in what the organization already knows | `brain` | tool names from that server's README |
| look at a web page | `browser` | needs Chromium; if Maurice cannot start it, say so |
| classify, score, or answer yes or no on a short text | `decision` | needs TypeSafe; if that key is missing, say so and stop |
| read the words in a picture | `ocr` | needs the hosted bridge; if it is missing, say so and stop |
| run a command on a machine they already named | `ssh` | only a published target; if none exists, say so and stop |

**A model needed during a local conversation.** If the person wants an AI
operation and Maurice has no usable model, tell them that Maurice can use their own
key without an AgentMaurice account. Direct them to **Connecter un modèle IA**
on the Maurice home page, then **Ma clé API**. Ask them to choose the provider and
model and enter the key in that masked form; never ask them to paste it in the
conversation. Keep the original task pending. Once the form reports a
successful test, resume that same task and prove the LLM call ran; a saved
secret reference alone is not proof of a usable model.

**Models.** List only the models this account may use:

```bash
maurice catalog llm list
```

Keep a row whose third column is `chat` or `decision`. Write that exact first
column as `llm_model` on the workflow. Maurice calls it. Do not ask the home
page to confirm that ref again. Do not choose a different one.

If the command says `account_not_paired` or `no authorized model`, stop. Ask
the person which API key to use, or which local model. Do not read
`https://llm.agentmaurice.app/v1/models`. Do not write a `hosted:` model.
Direct them to **Connecter un modèle IA** on the Maurice home page, then **Ma
clé API** or **Modèle local**. Never ask them to paste a key in the
conversation. A saved key is not proof: wait until they say the test
succeeded, then resume the same task. Each hosted use is paid with credits
they buy. No purchase happens by itself.

**Services the person already uses.** The connector directory is the full
Nango catalog, the same search as the Maurice home page. It is not a local MCP
server, and Edge does not provide it. Do not keep a short list in memory, and
do not download a provider file. Search it:

```bash
maurice catalog connector list --query "<service>"
```

The first column is the connector key. The third column is `api_key` or
`connect`. Propose one when the person’s words match a service and this
Maurice is paired with an AgentMaurice account. Name that one service in
everyday words. `connect` is the Connect button on the Maurice home page.
`api_key` is a masked field you open yourself, with the secret page steps in
SKILL.md: `maurice action request --kind secret_input`, then
`maurice viewer browser --human-action <action_id> --no-open` in the
background, then navigate to the exact printed loopback URL (full load of
host, port, and hash — not a hash-only edit on a previous secret page) in
the browser you already control. Confirm Ressource shows this secret before
handoff. Then `maurice action wait --id <action_id> --follow` until
`stored` or `cancelled`. Leave the HTML `page_url` unused. Never paste the
key.

Airtable does not open a login window. It uses a personal access token.
Open that masked page the same way. Do not ask them to paste the key in this
conversation, do not read a credential file, and do not print the key. The
key stays in the operating-system keyring. Connectors already set up are
listed apart, under « Déjà en place », so the person does not search the
full directory to find them. Once `action wait` reports `stored`, call
`airtable_list_bases`, `airtable_list_tables` (base_id) or
`airtable_list_records` (base_id and table). Find them with
`maurice tools list --query airtable` and call them with `maurice tools call`.
Do not print the key. Do not read the keyring, the `security` command, or
the secret yourself. Those tools already send the saved key.

For any other service, ask them to press Connect there. Wait for them. Do not
open the provider window, do not complete their login, and do not print a
session token. Each use is paid with credits they buy. After they say it is
connected, use the tools `maurice tools list` shows.

If the account is not paired, say the service needs that account on the home
page first. Do not deploy a server from the catalog as a stand-in, and do not
promise the service works without it.

`document`, `rag` and `search` are `one_compatible: false`. Do not deploy
them. Name what `requires` lists. `sidecar` is the launcher Maurice already uses.
Do not deploy it as a tool for the person. Do not invent a tool name. If the
catalog `tools` list is empty, read `<slug>/README.md`.

**Shipped by AgentMaurice.** When the inventory cannot do the job, discover
the server from the public catalog, not from the Console and not from memory:

```text
https://raw.githubusercontent.com/agentmaurice/mcp/main/catalog.json
```

Read `servers[]`. Keep rows with `one_compatible: true`. Match the person's
request to `description`, `tools[].name` and `tools[].description`. Skip
`one_compatible: false` (today `document`, `rag`, `search`): tell the person
which extra engine `requires` names, and do not promise that install. The
runtime image is `install_image` (`ghcr.io/agentmaurice/mcp/…`).

**Maurice deploys it.** The public GitHub catalog and this Maurice's instance registry
are separate. A compatible public server may be absent from the instance
registry. Use the CLI to inspect the public catalog, register the chosen
version under `public-<slug>` when needed, and ask Maurice to start its Docker
sidecar:

```text
maurice catalog mcp list --query <capability>
maurice catalog mcp info <slug>
maurice catalog mcp deploy <slug>
```

The deploy command uses the Agent ID from `maurice context current` by default;
pass `--deployment <id>` only for a different Agent you are authorized to
manage. The command waits for the chosen server to publish its tools by
default. Treat only `active` or `already_deployed` **with** `tools_ready: true`
as ready to use; registration without tools is still pending. A `failed`,
`timeout`, unknown status, or `tools_ready: false` stops the dependent call.
Inspect `maurice tools list` again before copying an exact tool name.
Do not `docker build`, do not `docker run` the image yourself, and do not fall
back to `maurice edge` or a public npm server. Never print a token, API key,
or credential file. If Docker is missing, the registry image is inaccessible,
or deployment fails, report the exact error and keep the rest of the work.
Do not claim the tool ran. Maurice itself does not need Docker to serve its home
page or internal tools.

Each server's tool names are in `https://github.com/agentmaurice/mcp` under
`<slug>/README.md`. The catalog often leaves `tools` empty; read the README
before calling. Do not invent sidecar flags or tool names.

**Then use it.** After `maurice tools list` shows the tool, copy that exact
name into a managed Workflow with `callTool` (see "Runtime tools from
code execution"). A MiniApp only sends an event to that Workflow. Prove the
call with a real execution.

## Bootstrap contract

Use the compact bootstrap returned by `maurice agent connect`. Ground every
operation in its organization, environment, Agent, policy, tool/model catalog,
contract hashes, warnings, and allowed commands. Do not request or paste the
full Doctor payload unless diagnosis needs it.

When the connected MCP surface exposes only search and call entrypoints,
discover the exact schema before invoking a tool. Never invent a tool name or
argument from this document.

## Agent Spec MCP family

The public V2 family is:

```text
inception_agent_spec_init
inception_agent_spec_pull
inception_agent_spec_check
inception_agent_spec_workflow_preview
inception_agent_spec_plan
inception_agent_spec_approve
inception_agent_spec_apply
inception_agent_spec_verify
inception_agent_spec_schema
inception_agent_spec_example
```

Use MCP schema and example retrieval when the CLI is unavailable. Preserve the
same lifecycle: check, immutable plan, explicit human approval, exact apply,
then verify. `inception_agent_spec_approve` is a human-principal operation and
is intentionally absent from a code-agent bootstrap. An agent or service
principal must not call or relay it; wait for the persisted plan to become
`approved` and use its matching `approval_id`.

Do not use direct Workflow or MiniApp administration for a resource whose
`management_mode` is `managed`. A compliant server returns
`managed_resource_requires_agent_spec_plan`.

## Diagnosis and observation

For a diagnosis:

1. Confirm the Agent and environment from bootstrap scope.
2. Read compact capabilities and contract hashes.
3. Request full Doctor only if the compact warning or failure needs it.
4. Compare desired component hashes with observed revisions.
5. Inspect provenance and blocking test results.
6. Report drift and propose a new plan; never reconcile implicitly.

For runtime observation, use the Workflow or MiniApp invocation surface
advertised by the bootstrap. Capture result, logs, trace, duration, token/cost
usage, and resource revision when available. Keep raw discovery documents and
secret-bearing headers out of user-facing output.

## Workflow LLM transport

Treat the Doctor `recipe_usage_rules.llm_call` block as the source of truth.
For native `llm_call` actions, configured OpenAI-compatible endpoints use
provider streaming and the runtime reassembles all deltas before storing the
text wrapper or parsed JSON at `output_key`. This transport is transparent to
downstream Workflow actions; never invent an action-level `stream` field.

A direct LLM `fetch()` inside Deno `code_execution` is a separate HTTP client
and does not inherit that behavior. With `stream: false`, parse the single JSON
response. With `stream: true`, consume `response.body` as SSE, concatenate
`choices[].delta.content`, handle the final usage chunk, and stop at `[DONE]`.
Do not call `response.json()` on a streaming response. Prefer native `llm_call`
when the Workflow only needs a completed text or JSON result.

## Runtime tools from code execution

Use the sandbox bridge only after resolving the exact tool name and argument
schema from the runtime inventory. Import it statically at the top of the code;
the Deno sandbox moves imports outside its async wrapper:

```ts
import { callTool } from './tools/nats_bridge.ts';

const items = {{ json .persist.contacts_items }};
if (!Array.isArray(items) || items.length === 0) {
  return { skipped: true, reason: 'no items' };
}

const result = await callTool('memory.entities.upsert', {
  entityType: 'contact',
  items,
  source: {{ json .persist.source }},
  writer: {{ json .persist.writer }}
});
return result;
```

The supported signature is
`callTool(name: string, args: Record<string, any> = {}): Promise<any>`. Do not
use a global helper or a dynamic import. Template rendering happens before Deno
execution: embed `{{ json .path }}` without surrounding quotes to produce a
native array, object, string, number, boolean, or null. Use the same pattern for
dynamic scalar values so quotes and line breaks cannot invalidate the code.

`callTool` returns `structuredContent` when present, otherwise parsed JSON from
the first text content block, otherwise the full tool result. Returning that
value stores it at the action `output_key`. Runtime scope and execution metadata are injected automatically;
do not add tenant or transport identifiers to tool
arguments unless the described tool schema explicitly requires them. Standard
tool calls have a 120-second bridge timeout. Validate the Workflow with a real
execution because static contract checking cannot prove a rendered value's
runtime type.

## Outbound network allowlist

Deno `code_execution` only receives the current Agent's `--allow-net` entries.
HTTP fetch tools use the same deployment-scoped list. Paths, query strings and
credentials are never stored; only host, scheme and effective port persist.

Inspect first, then mutate with the URL upsert when the user asked to allow a
callback:

```bash
maurice network allowlist list --json
maurice network allowlist allow-url --url "https://devmachine.example.com/callback"
```

Equivalent External Inception tools, scoped to the connected Agent:

```text
inception_allowlist_list
inception_allowlist_url_upsert
inception_allowlist_create
inception_allowlist_update
inception_allowlist_delete
```

`inception_allowlist_list` is readable in readonly mode. Mutations require a
guided credential. Prefer `allow-url` / `inception_allowlist_url_upsert` over
hand-derived host and port. Doctor reports the surface as
`allowlist_skills` with `inception_allowlist_*`; it does not replace `list`.

## Studio Doctor and CLI rails

For an existing Agent, run the compact Studio Doctor before opening a thread
or preparing a plan:

```bash
maurice studio doctor --agent <agent-alias> --env <environment> --json
```

Confirm the canonical target, server/CLI/contract/Skill compatibility,
required Studio capabilities, governance, and blocking diagnostics. The
response must advertise `runner_identity_contract` as
`agentmaurice.runner_identity/v1`; treat `runner_identity.actor` as the
credential-backed caller and `runner_identity.requester` as the principal on
whose behalf work exists. The `scope` must match the resolved target. Never
derive or replace these fields from a prompt, display name, `user_id`, or
command argument. Stop on `runner_identity_error.code: identity_unproven`.
For an agent or service principal, `can_approve` must remain `false`. Stop if
a blocking diagnostic covers `thread new`, `plan`, or `closeout`; use only
the redacted `next_actions[]` returned by the Doctor and never bypass it with
a direct HTTP call. Rerun the preflight after a context or version change.

For organization builders, run the organization Doctor before `studio thread
new --scope organization`. It must verify `builder_scope: organization`, one
Chief, plan v2, `create_agent`, closeout, and handoff. A diagnostic
`organization_builder_scope_required` means this session is Agent-scoped:
stop and follow only its redacted `next_actions[]`, without inventing aliases.

Use `maurice studio` for a persisted conversation with Studio. The draft,
revision, plan, and closeout live on the server-side thread. Use `maurice spec`
for direct Git-native authoring from reviewed project files. Do not mix its
provenance with a Studio plan. Use `maurice test studio` for a closed-loop test
suite and structured verdict.

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

For organization scope, thread creation targets the reserved Chief internally,
then hands off to the new Agent. On handoff or initialization failure, keep
committed `created_applications` and `created_agents`, return
`authoring_required`, and never recreate the Agent or thread.

Use `studio new-cycle` after a verified change, `studio fork` to explore an
immutable revision without moving the source thread, and `studio thread
archive` to hide a completed thread without deleting the Agent. Use
`studio say --record` and `studio replay` only with
`$schema: agentmaurice.studio_dialogue/v1`; assert structured facts, never
model prose, credentials, signed URLs, or approval identifiers.

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

## Explicit unmanaged sandbox

Before a direct administrative mutation, require all of the following:

- the user explicitly asked for sandbox work;
- the environment is not production;
- the server reports `management_mode: unmanaged`;
- the operation stays within the scoped Agent;
- no raw secret is written or returned.

If the resource is managed, stop and move the change into the Agent Spec
project. Adoption of sandbox work is a reviewed Agent Spec plan, not a flag on
the direct mutation.

## Failure handling

- `client_contract_incompatible`: upgrade the client before any mutation.
- `workspace_migrated_commit_required`: review and commit the migration, then
  rerun the intended command.
- `managed_resource_requires_agent_spec_plan`: use the Git-native rail.
- stale component or dependency: pull, merge/rebase, check, commit, replan, and
  request new approval.
- approval invalid or expired: produce a fresh plan and approval.
- verification mismatch: report partial effects and drift; do not declare
  success or reuse the approval.
