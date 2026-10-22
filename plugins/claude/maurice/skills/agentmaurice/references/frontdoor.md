# Maurice front door

Read this reference when a user asks to connect an assistant to One,
inspect the public MCP surface, or execute an authorized resource through
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
Use `execute` only for an exact discovered reference whose explanation permits
execution, with validated input. Every
execution requires an `idempotency_key`; reuse the same key when retrying the
same operation, and pass `expected_plan_hash`
when the caller is binding execution to a previously explained plan. Never
choose an individual runtime step or bypass the declared adapter and its policy.

`search` uses bounded local lexical matching over authorized resource
references, titles, and descriptions. It does not use embeddings or an LLM.
Its response includes `search_mode: local_lexical`, `limit: 50`, and
`truncated`; results are deterministically ranked and capped at 50. With no
query, business resources precede tools and historical plans. Use `--kind` to
filter large inventories; a truncated page is not evidence of missing rights.

`explain` includes the Workflow `title` and `description`, then a bounded
history projection: `recent_executions` (at most 10), `usage_summary`,
`history_scope: current_workflow_version_and_spec`, and `sample_window: 50`.
History is restricted to the same user, organization, scope, exact reference,
Workflow version, and Agent Spec. Drifted executions and other reference
versions are omitted. Usage medians use at most 50 completed, validated
results; an unknown value is `null`, never zero. Observed usage is an
observation, not a quote or a cap; absent execution effects remain absent.

### Approval descriptions

For an approved Workflow `tool_call`, keep the description clear about the action
and its scope; it is declared provenance, never an attestation that the effect
has happened. The human still reviews and approves the card, and Doctor
`checked/ok` only reports connection and catalog discovery; it proves neither
understanding nor approval.

### Bounded human approval

The existing one static `tool_call` action remains valid under an authorized
mandate, qualified zero cost, and `require_approval: true`; its first
`execute` requests one human approval for the immutable plan before admitting
a Job and has no external effect. A Workflow may use the intermediate
approval rail when it has 2–32 static `tool_call` actions with those same
constraints. Hanko users need current organization membership and published
Application access. `personal` uses the requester’s human decision; `org`
requires a current Hanko organization administrator; `both` requires the
personal decision followed by the organization decision. Competence is
server-attested and rechecked before effects, never inferred from a prompt
or a field supplied by the assistant. A local personal grant may carry a quota through
the owner grant command below. `explain` exposes the immutable `plan_hash`,
the initial plan, the leaf `effect_quota`, and the effective ancestor limit.

Each approved plan then yields one human card per gated Workflow step. Every
intermediate pending response includes `approval_phase: workflow_step`,
`action_id`, `approval_ref`, `workflow_action_id`, `occurrence_id`, `job_id`,
`execution_id`, the initial Workflow `plan_hash`, the card's `step_plan_hash`,
`expires_at`, and the effective `approval_surface`. All cards belong
to the same Job and execution. Resolve parameters at each gate from the
immutable Workflow/input context; never let a later card change the plan.
Dynamic runtime bindings such as `$binding`, `env://`, `secret://`,
`vault://`, and `am-bind:` are refused in approval profiles; declared
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

Initial pending responses also report the current `approval_phase` (`personal`
or `org`). For `both`, replay the unchanged operation after the first decision
to obtain the organization phase; do not collapse the two decisions. The same
human can act in both capacities when their current authority permits it, but
the assistant never gains that authority. A changed or revoked role blocks the
organization decision or subsequent effect.

Submandates revalidate their entire ancestor chain. Revoked, expired, missing,
cyclic or over-deep ancestors block the operation. A child cannot broaden the
parent’s scope, effects, duration or bounded budget. Workflow admission charges
the leaf and all ancestors in one transaction; sibling operations share the
parent budget. An exact replay consumes no second effect and still requires
live authority. Do not interpret the leaf’s remaining quota as permission to
exceed an ancestor’s budget. `effect_quota.scope` is `mandate`; `quota_chain`
lists every leaf/ancestor budget, and `effective_remaining_effects` is the
minimum finite remainder (or `null` only if every mandate is unbounded).

Present each exact card in the real human approval surface. For a local One
session, obtain its browser link with:

```bash
maurice viewer browser --human-action <action_id> --no-open
```

For a hosted One instance, give the human the instance link
`https://<instance-origin>/one/#/human-action/<action_id>`. They open it with
their own current Hanko session for that instance. The personal phase checks
the requester identity; the organization phase checks current administrator
authority in the exact organization. Never use the assistant grant token,
code-agent credentials or a fabricated human identity to open or decide a
card. If the human session or required authority is unavailable, leave the
card pending and report that blocker.

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

Qualify `search` and `explain` with distinct real calls after the Doctor
handshake. Doctor catalogue/reachability evidence alone does not qualify either
Workflow front-door operation.

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

Workflow references use the exact form
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

## Native references and effects

Copy references from discovery; never invent identifiers or infer identity:

| Reference | Behavior |
|---|---|
| `agent:<id>`, `application:<id>` | Read-only metadata; never an executable blanket permission. |
| `workflow:<agent>/<id>@<version>` | One durable governed Workflow Job. |
| `miniapp:<agent>/<id>@<version>` | A declared event on an existing same-Agent instance, bound to its state version and one declared Workflow action. |
| `tool:<agent>/<tool-name>` | A server-built single-action Job, with exact tool/schema/spec/input binding and human approval; no raw tool bypass. |
| `schedule:<agent>/<id>` | One immediate durable run using the immutable schedule/input snapshot; it does not edit the schedule. |
| `agent_spec:<agent>` | Prepare an immutable plan from validated authoring input, without applying it. |
| `agent_spec:<agent>/<plan>` | Submit the exact existing plan for review; its hash is binding. |
| `request:<kind>` | Submit a typed human request only if that effect is explicitly in the mandate. |
| `pending_action:<id>` | Observe a human card; never resolve it as the assistant. |

A tool adapter reuses the durable Workflow Job and `workflow_run` budget. It
checks the actual runtime environment, direct-call policy, and zero-cost
qualification before creating a card. It never provisions a Workflow resource
or accepts a caller-built internal Job proof. Changed definitions, revoked
grants or production policy failures block before the effect. Input text that
looks like a template stays literal data.

Native MiniApp input and state are frozen with a durable request reservation;
replay returns the same result even after state advances. Changed state/input,
Agent Spec, tool permissions, or schedule bindings refuse before another effect.
An unsupported event or profile is a refusal, never a fallback to raw execution.

Agent Spec preparation requires the explicit `approve_plan` mandate effect.
Its `pending_approval` response carries `plan_id`, `plan_hash`, `action_id`,
`next_action: review_plan_in_studio`, and `studio_approval_required: true`.
Resolving the request card does not approve or apply the native Plan: the human
must review it in Studio through the existing authoring rail. Application
publication grants no Studio write permission. On Hanko, an explicitly chosen
Agent scope is available only to a current organization administrator; it has
`effects: [approve_plan]`, personal review, no Application target and no other
operation. The live admin role and exact Agent are checked again before plan
creation. The assistant never approves.

`result_kind` distinguishes native results from the legacy Workflow envelope;
request results carry `request_id` (`completed` requires a recorded effect;
`accepted` alone is not a completed effect), while completed MiniApp results carry
`job_id`, `instance_id`, `state_version`, and the redacted state/result. Do not
require a Workflow `execution_id` in every native result. Discovery and these
shape descriptions are not evidence of a completed runtime qualification.

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
  --duration-hours 24 \
  --max-effects <N> \
  --output <private-path>/assistant.token
maurice frontdoor revoke --data-dir <one-data-dir> \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice <grant-id>
```

Use at most one of `--ref <workflow-ref>` and `--application <application-id>`;
they are mutually exclusive: `maurice frontdoor grant --application
<application-id>` must not also receive `--ref`. An Application grant
admits only that Application’s published resources. Its members, roles, and
tool grants are revalidated against the Application, so an Application grant
cannot add rights beyond those existing permissions. Grant list and revoke
metadata retain the Application id/title, including when the Application is
inactive. An Application observation is not permission to execute its resources.

The grant is the assistant's authority; it is distinct from the local
provider/owner identity. Revoke the grant when the assistant must lose access.
Do not print, paste, or put the token in an argument, shared configuration, or
log. The `--organization` scope identifies the owner organization; `--ref`
keeps the allowed Workflow reference narrow. Do not invent a broader scope
flag or infer identity from the command line. `--max-effects N` is available
for an execution grant and bounds its shared admitted effects;
`0` keeps the existing unbounded behavior, and a positive value requires
`--execute`. The quota unit is `workflow_run`, charged once at Job admission.
Replays of the same idempotency key are free; pending initial approval is free;
an admitted failure or cancellation is not refunded. `explain` reports the
leaf `effect_quota` object with `max_effects`, `used_effects`,
`remaining_effects` (an integer or `null` when unbounded), `exhausted`,
`charged_at: admission`, and `refund_policy: none`. A `quota_exhausted`
response must not be bypassed by minting a new grant or starting a new
idempotency key.

### One home: Brancher mon assistant local

The One home entry point is a local personal path that requires no provider
account. It can grant access to all local resources, one exact Workflow, or one
Application’s published resources, with either discover/explain permission or
execute permission. The available durations are 1 hour, 24 hours, and 7 days;
an execution grant may carry a quota from 0 through 1000 effects. The home creates the bearer token
automatically in the private `assistant-grants` keystore with file mode `0600`.
It never returns the token to the browser. After creation it displays only the
loopback URL, the token-file path, and an explicit command using
`maurice assistant connect codex` or `maurice assistant connect generic` with
`--config-file`; use the list and revoke controls to manage grants. Application
metadata remains visible for listing and revocation, including for inactive
Applications. This no-account path is distinct from the Hanko path below.

The creation form lists the authorized operations explicitly. Omitted `effects`
keeps the existing `workflow_run` default; old grants gain no new effect.
`--effects workflow_run,approve_plan,expense_note` selects only the named
operations. Local grants use `personal` approval only. An exact Workflow or
Application scope cannot silently become a Studio authoring scope.
For `expense_note`, require finite positive `--max-effects`, positive
`--expense-per-use-max-minor` (at most 1000000000), and
`--expense-currency EUR` (three uppercase letters). Minor units are explicit:
100 EUR minor units means one euro. Recording a note never makes a payment.
The generic `request:approve_plan` cannot stand in for the native plan adapter.
`request:oauth_connect` and `request:secret_input` currently refuse execution
without an attested collector; discovering their type grants no collection
permission. Do not claim those providers are connected.
All selected effects share the quota; discovery/read-only permission creates
no execution capability. Never create another grant to evade a spent budget.

On a Console-enrolled VM, an authenticated Hanko human chooses a published
Application within their current rights. The form can choose `personal`,
`org`, or ordered `both` approval. It shows the token once, in that session,
without saving it in browser storage; store it in the private client token
file, hide it, and keep it out of screenshots/logs. Current membership,
Application access, and the human approver’s authority are revalidated.
Unready VM profiles prohibit new public grants while preserving revocation.
A local owner token or assistant token is not a Hanko human session.

The stdio bridge connects to an already running MCP endpoint and does
not start One or any service:

```bash
maurice frontdoor-mcp-stdio \
  --endpoint http://127.0.0.1:<mcp-port>/mcp/maurice \
  --token-file <private-path>/assistant.token
```

`--token-file` overrides the legacy `MAURICE_MCP_TOKEN` environment path. The
endpoint must be literal loopback HTTP or verified HTTPS at `/mcp/maurice`
(or the API route `/api/v2/mcp/maurice`). HTTPS uses system trust, no redirects
and no environment proxy. Never disable certificate validation or publish a
workstation to imitate a VM.

For MauriceCLI API calls to a private-CA deployment, set
`MAURICE_TLS_CA_FILE=<private-ca-pem>` for that process. The client appends this
CA to system roots, verifies the hostname, preserves the normal environment
proxy, and refuses a missing or invalid PEM before networking. This option
does not alter system trust or configure the MCP stdio bridge, whose transport
remains separate. Never substitute an insecure TLS flag.

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
catalogue only. It does not call a Workflow or prove
the whole assistant-to-runtime path. If either option is omitted, the check is
not run or is invalid; do not silently fall back to an environment token.

For HTTPS, also read `vm_profile_readiness.checked`, `ok`, and `public_ready`.
This is separate from the MCP catalogue. A positive result requires fresh,
server-observed VM profile evidence bound to the endpoint and organization:
Console enrollment, Hanko-only auth, loopback API, UFW, listeners, Docker
port bindings and verified TLS. Missing or inaccessible evidence blocks the
public-ready verdict. A local HTTP endpoint does not run this VM check.
Neither result proves an Application scope, Workflow effect, human approval,
or a real external assistant session; qualify those separately.

## Native discovery and audit

MiniApp `explain` observes the published event and its current gesture policy;
it does not accept candidate event input. Pass the event input to `execute`,
which binds and validates the actual action at admission. Do not present this
metadata-only explanation as an input-bound execution preview.

Use returned references, never display names: `agent:<id>`,
`application:<id>`, `miniapp:<agent>/<id>@<version>`, `tool:<agent>/<name>`,
`schedule:<agent>/<id>`, `agent_spec:<agent>/<plan-id>`, and
`pending_action:<id>`. An Agent or Application observation is read-only.
Application scope rechecks current membership, published surfaces and tool
rights. Removing all tool rights can leave the Application metadata visible
while removing its executable references. An Application grant cannot expose
an Agent-wide Agent Spec plan. `search` and `explain` must create no effect.

The Workflow admission persists assistant actor, requester, subject, mandate,
reference and plan hash with the Job; journal events bind that delegation to
policy and Agent Spec hashes. Verify the SHA-256 chain against an independently
retained tail when detecting truncation or wholesale replacement matters.
Legacy events without that receipt are not retroactively attested.

Per-token dispatch is limited to a burst of 60 calls, replenished at one call
per second; `rate_limited` is an operational refusal, not an approval. The
bucket is process-local and resets on restart. Revocation is rechecked before
dispatch even when the bucket is exhausted. `quota_exhausted` and
`approval_denied` remain authorization failures; do not retry under another
identity or mint a grant to bypass them.

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
