# Expert operations

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
