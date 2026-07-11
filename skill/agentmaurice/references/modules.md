# Skills and Modules

Load this reference when packaging reusable executable resources or migrating
an old package that mixes instructions and runtime content.

## Definitions

A **Skill** is an instruction package for a coding agent. It may contain
procedures, references, deterministic helper scripts, and authoring assets. It
does not execute inside the AgentMaurice runtime and cannot be used as a
Workflow action.

A **Module** is a versioned executable package. It may contribute Workflows,
MiniApps, runtime schemas, assets, and documentation. Agent Specs and test
plans stay in the consuming Agent project. Installation of a Module changes
desired state and therefore produces an immutable plan that requires human
approval before apply.

The Skill Catalog contains instruction-only Skills. The Module Catalog
contains executable Modules with source provenance, resolved commit, version,
and content hash.

## Migration of a mixed package

Classify every file before conversion:

- instructions and agent-facing references -> Skill;
- Workflow, MiniApp, runtime schema, executable asset -> Module;
- Agent Spec or test plan -> consuming Agent project, never Module;
- raw credential or secret -> reject and remove from the package;
- ambiguous executable intent -> stop and report an ambiguous migration.

Convert the executable resources into the Agent Spec V2 directory structure
inside the Module. Keep the instruction-only Skill separate and link to the
Module by public catalog identity, never by copying executable definitions into
the Skill.

The public Module contract is V2-only:

```text
module.yaml
agents/main/workflows/<workflow-id>.json
agents/main/miniapps/<miniapp-id>.json
```

`module.yaml` requires `$schema: agentmaurice.module/v2` and
`schema_version: 2`. Each `provides.actions` or `provides.queries` entry points
to an explicit `workflow_id` and `workflow_version`; each `provides.apps`
entry points to a `miniapp_id` and `miniapp_version`. A Module must not contain
an Agent Spec, a test plan, or any V1 resource directory, discriminator, or
identifier field.

Run Module validation and tests before publishing. Review source URL, resolved
commit, version, module hash, capabilities, and credential references. Never
publish or install from a mutable source without resolved provenance.

## Installation lifecycle

Use the commands exposed by MauriceCLI:

```text
maurice module init <key> [--dir <path>] [--version <version>]
maurice module validate --file <path>/module.yaml
maurice module test --file <path>/module.yaml
maurice module publish --file <path>/module.yaml
```

Preserve this lifecycle:

```text
validate -> test -> publish/import -> add to desired state
         -> plan -> human approval -> apply --tests auto -> verify
```

Do not bypass Agent Spec ownership by installing executable resources through
a Skill operation. If a Module contributes resources to a managed Agent, the
resulting plan must name the affected components and their preconditions.
