# AgentMaurice Skill

Public repository for an English-language AgentMaurice skill that helps an AI:
- inspect deployments safely
- operate AgentMaurice as a workflow backend and a mini-app backend
- verify recipe runtimes, viewer bootstrap, and OpenUI-backed mini-app delivery
- use the Workspace Control MCP gateway
- fall back to the `maurice` CLI
- run governed meta-recette and recipe workflows

## What This Repository Contains

- [`skill/agentmaurice`](./skill/agentmaurice): the reusable skill itself
- [`docs/install.md`](./docs/install.md): a short installation guide
- [`examples/diagnose-deployment.md`](./examples/diagnose-deployment.md): ready-to-copy diagnostic workflow
- [`examples/governed-meta-recette-change.md`](./examples/governed-meta-recette-change.md): ready-to-copy governed change workflow
- [`examples/create-or-update-recipe.md`](./examples/create-or-update-recipe.md): ready-to-copy recipe workflow
- [`examples/verify-recipe-backend.md`](./examples/verify-recipe-backend.md): ready-to-copy workflow backend verification
- [`examples/verify-mini-app-openui-backend.md`](./examples/verify-mini-app-openui-backend.md): ready-to-copy mini-app and OpenUI verification

## Who This Is For

Use this skill if you want an AI assistant to operate AgentMaurice through:
- the Workspace Control MCP gateway
- the External Inception MCP gateway
- the `maurice` CLI

This repository is aimed at teams who want a portable, publishable skill instead of a private skill buried inside a mono-repo.

## Core Design

The skill follows a few simple rules:
- Doctor first
- prefer Workspace Control over lower-level paths
- treat AgentMaurice as two backend runtimes: `mode=recipe` and `mode=app`
- treat OpenUI as an optional presentation layer over the mini-app runtime, not as the runtime source of truth
- use governed prepare/apply flows for changes
- present plans before apply
- prefer meta-recette workflows for user-intent changes
- run lightweight verification flows before deep mutations when the user asks for runtime confidence

## Quick Start

1. Install the skill folder from [`skill/agentmaurice`](./skill/agentmaurice) into your assistant's skills directory.
2. Make sure your environment has either:
   - a working AgentMaurice MCP connection
   - or a working `maurice` CLI configuration
3. Start with one of the examples in [`examples`](./examples).

## Recommended First Workflows

- Diagnose a deployment:
  [`examples/diagnose-deployment.md`](./examples/diagnose-deployment.md)
- Verify a recipe backend:
  [`examples/verify-recipe-backend.md`](./examples/verify-recipe-backend.md)
- Verify a mini-app and OpenUI backend:
  [`examples/verify-mini-app-openui-backend.md`](./examples/verify-mini-app-openui-backend.md)
- Prepare and apply a governed meta-recette change:
  [`examples/governed-meta-recette-change.md`](./examples/governed-meta-recette-change.md)
- Create or update a recipe from user intent:
  [`examples/create-or-update-recipe.md`](./examples/create-or-update-recipe.md)

## Directory Layout

```text
agent-maurice-skill/
├── README.md
├── docs/
│   └── install.md
├── examples/
│   ├── create-or-update-recipe.md
│   ├── diagnose-deployment.md
│   ├── governed-meta-recette-change.md
│   ├── verify-mini-app-openui-backend.md
│   └── verify-recipe-backend.md
└── skill/
    └── agentmaurice/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── backend-verification.md
            ├── commands.md
            ├── mcp-tools.md
            └── workflows.md
```

## Notes

- The skill content is intentionally concise.
- Detailed operational material lives in the reference files.
- The examples are repository documentation, not part of the skill payload itself.
