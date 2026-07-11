# Agent Spec V2 authoring

Load this reference when editing an Agent Spec project. Retrieve the exact
embedded JSON Schema with `maurice spec schema`; this reference describes
boundaries and invariants rather than duplicating the schema.

## Project layout

```text
agentmaurice.project.json
agentmaurice.lock.json
environments/<environment>.json
agents/<agent-alias>/
├── agent-spec.json
├── workflows/<workflow-id>.json
├── miniapps/<miniapp-id>.json
└── tests/test-plan.json
```

Use public Agent vocabulary in authoring files: `agent_id`, `agent_alias`, and
`agent_spec_id`. Do not add runtime deployment identifiers to V2 documents.

Each JSON document must contain its embedded-contract identifier and
`schema_version: 2`. Documents are closed: unknown properties are errors unless
the schema intentionally declares an open map.

## Resource boundaries

Keep `agent-spec.json` limited to intent and desired state. Reconstruct the
Workflow and MiniApp sets from their directories. Do not copy resource lists,
Doctor snapshots, tool discovery, editor state, timestamps, or calculated
hashes into desired state.

Store one Workflow or MiniApp per file:

- require `kind: workflow` in `workflows/`;
- require `kind: miniapp` in `miniapps/`;
- compose Workflows with `workflow_call`;
- do not model a Skill as an action;
- use reference objects for secrets;
- use versioned capabilities for inter-Agent dependencies.

When a MiniApp causes a business side effect, call a Workflow. Keep business
logic, retry policy, authorization, and observability in that Workflow rather
than duplicating them in the MiniApp event handler.

## Ownership

An Agent Spec owns the resources marked `managed` by its applied revision.
Change those resources only by editing the Agent Spec project and applying an
approved plan.

A direct administration operation is valid only when the server explicitly
reports the target as an `unmanaged` sandbox. Adoption into managed state and
release back to unmanaged state are explicit plan actions.

Entries in `policy_references` are managed Policy attachments, surfaced as
`policy:<reference>` components in a plan. Agent Spec owns the attachment and
its revision, hash, and resource version; it does not author the external
policy provider's content. Add or remove the reference through an approved
plan. The root release manifest is server-owned evidence and must never be
written into the Git workspace.

Use per-component versions returned by `spec plan`. Two changes to disjoint
components may proceed concurrently; a changed component or dependency makes
the affected plan stale.

## Contract-led editing

Prefer a locally embedded schema over memory:

```bash
maurice spec schema agent-spec --json
maurice spec schema workflow --json
maurice spec schema miniapp --json
maurice spec schema test-plan --json
maurice spec example workflow --json
```

Run `maurice spec check --json` after every coherent edit. Use its JSON pointer
and diagnostic code to repair the file. Do not weaken or bypass validation.

## Safe synchronization

Use `maurice spec pull` to synchronize remote desired state. It must refuse to
overwrite locally modified managed files. Keep changes inside the current
Agent subtree and preserve unrelated Agents and environments in shared
manifests.

After a V1-to-V2 migration, inspect the report and commit the migration alone
before adding functional changes. Restore from
`.git/agentmaurice/migrations/<migration-id>` only during the declared cutover
recovery window.
