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
```

From External Inception, use the equivalent read-only tools directly:

1. `inception_tools_list` for the authoritative runtime inventory;
2. `inception_tools_resolve` for an intent or capability;
3. `inception_tools_describe` for the exact schema and invocation policy;
4. execute directly only when `invocation.direct.allowed` is true;
5. otherwise declare the call in a managed Workflow when
   `invocation.workflow.allowed` is true;
6. report a missing capability only after an explicit `not_found` result.

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
