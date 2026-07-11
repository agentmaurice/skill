# AgentMaurice Skill

Instruction package for coding agents that author and operate AgentMaurice
Agent Specs through the public Git-native V2 workflow.

The skill gives Codex, Claude Code, Cursor, Windsurf, and generic clients one
governed path:

```text
connect -> init -> edit -> check -> commit -> plan
        -> approval by a separate human principal -> apply -> verify
```

## Public model

- Agent Spec: declarative desired state for one Agent.
- Agent: deployed product resource.
- Workflow: executable business process.
- MiniApp: interactive runtime surface.
- Skill: instructions for a coding agent; never a runtime action.
- Module: versioned executable package contributing Workflows, MiniApps,
  runtime schemas, assets, and documentation. Agent Specs and test plans stay
  in the consuming Agent project.

Managed Workflows and MiniApps change only through an approved Agent Spec plan.
Direct administration remains limited to a sandbox explicitly reported as
unmanaged.

## Package

The installable package is [`skill/agentmaurice`](skill/agentmaurice):

```text
skill/agentmaurice/
├── SKILL.md
├── skill-version.json
├── agents/
│   └── openai.yaml
└── references/
    ├── agent-spec-v2.md
    ├── app-delivery.md
    ├── credential-hygiene.md
    ├── end-user-auth.md
    ├── expert-operations.md
    ├── frontend-starter.md
    ├── generated/
    │   ├── agent-spec-v2.generated.md
    │   ├── manifest.json
    │   └── examples/*.json
    └── modules.md
```

`SKILL.md` contains only the nominal authoring rail and stop conditions.
Contract boundaries, expert operations, Module rules, credential hygiene, and
delivery procedures are loaded from references only when needed.

The contract generator copies its hash-bound reference and nine canonical
examples into `references/generated/`; `skill-version.json` inventories every
file and pins the same bundle hash as MauriceCLI. Full JSON Schemas remain
on-demand through the installed client:

```bash
maurice spec schema workflow --json
maurice spec example workflow --json
```

## Install

See [`docs/install.md`](docs/install.md). MauriceCLI normally installs the
embedded package during `maurice agent connect --skill auto` for clients with a
native skill format.

## Validate

From the sibling `test-maurice` repository:

```bash
task test:skill:content-lint
task test:code-agent:bench
```

The first command validates the package and its relative links. The second
validates the isolated two-turn benchmark harness. Real Codex and Claude Code
runners use the same event protocol after their client and model versions are
pinned.

AgentMaurice is proprietary software. This instruction package does not change
the licensing status of the platform.
