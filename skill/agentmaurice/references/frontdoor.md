# Maurice front door

Read this reference when a user asks to connect an assistant to a local One,
inspect the public MCP surface, or call a published Workflow through
`maurice.search`, `maurice.explain`, or `maurice.execute`.

## Public rail

The front door is the MCP server `maurice` with exactly three public tools:

```text
maurice.search
maurice.explain
maurice.execute
```

Use `search` to discover only references visible to the bearer. Use `explain`
for the reference, schemas, policy, dry-run/plan information, and plan hash.
Use `execute` only for an exact Workflow reference and a validated input. Every
execution requires an `idempotency_key`; reuse the same key when retrying the
same operation, and pass `expected_plan_hash`
when the caller is binding execution to a previously explained plan. Never
choose an individual runtime step or call a raw tool behind a Workflow.

### Bounded human approval

The existing one static `tool_call` action remains valid for a local
`personal` mandate, zero cost, and `require_approval: true`; its first
`execute` requests one human approval for the immutable plan before admitting
a Job and has no external effect. A local Workflow may use the intermediate
approval rail when it has 2–32 static `tool_call` actions with those same
constraints. Hosted, organization, `both`, quota, child, and other dynamic
scopes remain refused. `explain` exposes the immutable `plan_hash` and the
initial plan.

Each approved plan then yields one human card per gated Workflow step. Every
intermediate pending response includes `approval_phase: workflow_step`,
`action_id`, `approval_ref`, `workflow_action_id`, `occurrence_id`, `job_id`,
`execution_id`, the initial Workflow `plan_hash`, the card's `step_plan_hash`,
`expires_at`, and `approval_surface: personal`. All cards belong
to the same Job and execution. Resolve parameters at each gate from the
immutable Workflow/input context; never let a later card change the plan.
Dynamic runtime bindings such as `$binding`, `env://`, `secret://`,
`vault://`, and `handle:sam-bind:` are refused in approval profiles; declared
input and parameters are resolved before any effect.
No gated effect runs without a distinct human decision for that card.

The initial card shows declared parameters; each step card shows parameters
resolved at that gate. Every card also carries a server-side redacted input
preview capped at 4 KiB; larger previews are refused. Key masking is
presentation hygiene, not a free-text secret detector. Each card expires at
`min(15 minutes, grant expiry, mandate expiry, native gate expiry when
configured, Job deadline)`; the existing 300-second deadline remains. Expiry
is rechecked before every new effect. An acquired result may still be read
after its approval TTL.

Present each exact card in the real approval surface with:

```bash
maurice viewer browser --human-action <action_id> --no-open
```

The assistant must leave every decision to the human and never approve for
them. `explain` on `pending_action:<id>` only observes that card. Replaying
`execute` keeps the original Workflow `ref` (never `approval_ref`) and the same
input, `idempotency_key`, and `expected_plan_hash`; it advances the same Job
and execution to the next gate. Changed input with the same `idempotency_key`,
or a changed plan, is a conflict. A new key starts a new explicit operation
and may create a new Job. Refused, revoked, expired, or ambiguous state blocks without replay;
after restart, reconcile the persisted Job/cards before continuing. Doctor's
`checked/ok` covers only read-only `initialize` and `tools/list`; it never
proves a plan, gate, human decision, Job, or execution.

### Declared Workflow results

A Workflow that declares both `output` and `output_schema` returns its declared
business result. The schema is pinned in the AgentJob when the Workflow is
admitted from the applied Agent Spec; `explain` reports that effective schema.
The result is limited to 64 KiB. Sensitive keys are redacted recursively before
the result is returned. If redaction makes the result invalid against the
pinned schema, the response is blocked without returning the result content.

The legacy Workflow shape without `output_schema` keeps the M0 contract
`{"ok":true}`. No internal execution context is propagated, and this does not
add a new Workflow kind, LLM capability, or action surface. A retry with a new
Job for this result profile is refused; replay of the same operation with the
same idempotency key remains supported. This documents the contract only and
is not runtime qualification evidence.

The first contract is Workflow-only. References use the exact form
`workflow:<agent-id>/<workflow-id>@<version>`. Unsupported reference kinds,
out-of-scope references, invalid input, invalid grants, approval requirements,
plan hash mismatches, and idempotency conflicts remain typed errors. A local
Workflow can legitimately return `application: null`: this means no
Application owns the surface, not that the Workflow is unauthenticated.

The public CLI mirrors those three tools. Keep the endpoint and token file
explicit, and supply the operation fields on `execute`:

```bash
maurice search --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --token-file <private-path>/assistant.token --query "<term>"
maurice explain 'workflow:<agent-id>/<workflow-id>@<version>' \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --token-file <private-path>/assistant.token
maurice execute 'workflow:<agent-id>/<workflow-id>@<version>' \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --token-file <private-path>/assistant.token \
  --input-file <private-path>/input.json \
  --idempotency-key <operation-id> --expected-plan-hash <sha256-plan-hash>
```

## Local grant and bridge

The local One provider does not require an account. The owner issues a separate
assistant grant, optionally narrowed to an exact Workflow reference, and keeps
the token in a private file:

```bash
maurice frontdoor grant \
  --data-dir <one-data-dir> \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --organization <organization-id> \
  --ref 'workflow:<agent-id>/<workflow-id>@<version>' \
  --execute \
  --output <private-path>/assistant.token
maurice frontdoor revoke --data-dir <one-data-dir> \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice <grant-id>
```

The grant is the assistant's authority; it is distinct from the local
provider/owner identity. Revoke the grant when the assistant must lose access.
Do not print, paste, or put the token in an argument, shared configuration, or
log. The `--organization` scope identifies the owner organization; `--ref`
keeps the allowed Workflow reference narrow. Do not invent a broader scope
flag or infer identity from the command line.

The stdio bridge connects to an already running loopback MCP endpoint and does
not start One or any service:

```bash
maurice frontdoor-mcp-stdio \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --token-file <private-path>/assistant.token
```

`--token-file` overrides the legacy `MAURICE_MCP_TOKEN` environment path. The
endpoint must remain a literal loopback HTTP URL at `/mcp/maurice`.

## Bounded Doctor check

Use both options together and request JSON:

```bash
maurice doctor \
  --data-dir <one-data-dir> \
  --mcp-endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --mcp-token-file <private-path>/assistant.token \
  --json
```

The front-door portion performs authenticated MCP initialize and `tools/list`
only, with a five-second timeout. Read `mcp_frontdoor.checked` and
`mcp_frontdoor.ok`, plus the redacted `error` or `note`; do not infer success
from human output. `ok: true` proves local reachability and the expected
catalogue only. It does not call a Workflow, validate a VM profile, or prove
the whole assistant-to-runtime path. If either option is omitted, the check is
not run or is invalid; do not silently fall back to an environment token.

This reference does not qualify a Workflow, a VM, or an external assistant.
Those require the separate runtime audit and the applicable AgentMaurice
approval rail.

## Assistant connection contract

For an already running local One, the assistant connection rail is explicit:

```bash
maurice assistant connect codex \
  --config-file <private-path>/codex-config.toml \
  --token-file <private-path>/assistant.token \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --name maurice
maurice assistant connect generic \
  --config-file <private-path>/mcp.json \
  --token-file <private-path>/assistant.token \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --name maurice
```

`--token-file` is required and remains private; `--endpoint` defaults to the
loopback `/mcp/maurice` endpoint and `--name` defaults to `maurice`. The command
first performs authenticated MCP initialize and `tools/list` with a five-second
timeout, then writes the configuration atomically. It creates no grant, does
not start One, does not configure another client, and does not inspect a VM.
The Codex output is TOML (`mcp_servers.<name>`); the generic output is JSON
(`mcpServers[<name>]`). Existing identical entries are a no-op after the
preflight. A different existing entry is a conflict and is refused; all other
entries are preserved. No bearer value is copied into configuration: clients
must reference the private token file according to their format.
