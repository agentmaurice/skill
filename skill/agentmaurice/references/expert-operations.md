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
required Studio capabilities, governance, and blocking diagnostics. For an
agent or service principal, `can_approve` must remain `false`. Stop if a
blocking diagnostic covers `thread new`, `plan`, or `closeout`; use only the
redacted `next_actions[]` returned by the Doctor and never bypass it with a
direct HTTP call. Rerun the preflight after a context or version change.

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
