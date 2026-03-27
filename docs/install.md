# Install the AgentMaurice Skill

This repository keeps the reusable skill in:

```text
skill/agentmaurice
```

Install that folder into the skills directory used by your assistant.

## Option 1: Codex

Copy:

```text
skill/agentmaurice
```

to:

```text
~/.codex/skills/agentmaurice
```

## Option 2: Claude-style repository skills

If your setup uses repository-local skills, copy:

```text
skill/agentmaurice
```

to:

```text
.claude/skills/agentmaurice
```

## Option 3: Any file-based skill system

Place the `agentmaurice` folder into the directory where your assistant expects skill folders with a `SKILL.md` root file.

## Minimum Runtime Requirements

The skill is useful only if at least one of these is available:

- Workspace Control MCP access
- External Inception MCP access
- a configured `maurice` CLI

## CLI Install

If you want to use the CLI path, install `maurice` from:

- [agentmaurice/mauricecli](https://github.com/agentmaurice/mauricecli)

The exact installation method depends on that repository's release and packaging strategy. Once installed, the skill expects the `maurice` binary to be available in `PATH`.

## Recommended MCP Setup

Workspace Control usually looks like this:

```json
{
  "command": "npx",
  "args": [
    "mcp-remote@latest",
    "http://localhost:5000/api/v1/organization/<org_id>/mcp/external/workspace",
    "--header",
    "Authorization: Bearer sk_maurice_orgctrl_...",
    "--header",
    "X-AgentMaurice-Workspace-Role: admin"
  ]
}
```

## Recommended CLI Bootstrap

```bash
maurice ping --json
maurice whoami --json
maurice workspace auth issue --organization <org_id>
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace tools list
```

## First Validation

After installation, a good first check is:

- ask the assistant to use the AgentMaurice skill for a deployment diagnostic
- or ask it to bootstrap the current workspace contract

Examples are in:
- [`../examples/diagnose-deployment.md`](../examples/diagnose-deployment.md)
- [`../examples/governed-meta-recette-change.md`](../examples/governed-meta-recette-change.md)
