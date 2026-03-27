# AgentMaurice Skill

Public repository for an English-language AgentMaurice skill that helps an AI:
- turn a raw app idea into a deployed AgentMaurice application
- model that application as one or more deployments with one or more meta-recettes
- choose and describe a public client frontend starter when needed
- inspect deployments safely
- operate AgentMaurice as a workflow backend and a mini-app backend
- verify recipe runtimes, viewer bootstrap, and OpenUI-backed mini-app delivery
- use the Workspace Control MCP gateway
- fall back to the `maurice` CLI
- run governed meta-recette and recipe workflows

## What You Can Do With It

Use this skill when you want an AI in Claude Code, Codex, or a similar agentic environment to:
- read an application idea or a repository description
- map that idea to AgentMaurice deployments and blueprint slices
- choose whether each slice should be a mini-app or a workflow backend
- describe end-user authentication such as Firebase, Supabase, or generic OIDC
- choose a frontend starter such as `agent-maurice-viewer`
- prepare, preview, verify, and deploy the resulting application

The intended outcome is not only a drafted spec. The intended outcome is a usable AgentMaurice app or backend, plus a clear access and verification plan.

## What This Repository Contains

- [`skill/agentmaurice`](./skill/agentmaurice): the reusable skill itself
- [`docs/install.md`](./docs/install.md): a short installation guide
- [`docs/agentmaurice-app-format.md`](./docs/agentmaurice-app-format.md): the official `agentmaurice.app.md` format
- [`templates/agentmaurice.app.md`](./templates/agentmaurice.app.md): the official V1 application template
- [`examples/use-viewer-demo-as-client-app.md`](./examples/use-viewer-demo-as-client-app.md): ready-to-copy public frontend starter workflow
- [`examples/use-viewer-embed-in-existing-site.md`](./examples/use-viewer-embed-in-existing-site.md): ready-to-copy embed workflow
- [`examples/diagnose-deployment.md`](./examples/diagnose-deployment.md): ready-to-copy diagnostic workflow
- [`examples/firebase-end-user-auth.md`](./examples/firebase-end-user-auth.md): ready-to-copy Firebase auth description
- [`examples/supabase-end-user-auth.md`](./examples/supabase-end-user-auth.md): ready-to-copy Supabase auth description
- [`examples/from-idea-to-mini-app.md`](./examples/from-idea-to-mini-app.md): ready-to-copy app builder workflow
- [`examples/from-idea-to-workflow-backend.md`](./examples/from-idea-to-workflow-backend.md): ready-to-copy workflow backend builder
- [`examples/from-app-description-directory.md`](./examples/from-app-description-directory.md): ready-to-copy repository-driven app builder workflow
- [`examples/preview-verify-deploy-app.md`](./examples/preview-verify-deploy-app.md): ready-to-copy preview and deploy workflow
- [`examples/governed-meta-recette-change.md`](./examples/governed-meta-recette-change.md): ready-to-copy governed change workflow
- [`examples/create-or-update-recipe.md`](./examples/create-or-update-recipe.md): ready-to-copy recipe workflow
- [`examples/verify-recipe-backend.md`](./examples/verify-recipe-backend.md): ready-to-copy workflow backend verification
- [`examples/verify-mini-app-openui-backend.md`](./examples/verify-mini-app-openui-backend.md): ready-to-copy mini-app and OpenUI verification

## Who This Is For

Use this skill if you want an AI assistant to operate AgentMaurice through:
- the Workspace Control MCP gateway
- the External Inception MCP gateway
- the `maurice` CLI

If you want to use the CLI path, install it from [agentmaurice/mauricecli](https://github.com/agentmaurice/mauricecli).

This repository is aimed at teams who want a portable, publishable skill instead of a private skill buried inside a mono-repo.

It is especially useful if you want a user to be able to say:

```text
Here is my app idea. Build it on AgentMaurice, choose the right runtime,
guide me only on blocking questions, and tell me how to access the result.
```

## Core Design

The skill follows a few simple rules:
- Doctor first
- start from user intent, not from internal implementation nouns
- prefer Workspace Control over lower-level paths
- treat a meta-recette as an application blueprint slice, not as the whole application
- expect a real application to span one or more deployments and one or more meta-recettes
- treat the client frontend repo as a separate public artifact when the user needs a branded application front
- prefer `agent-maurice-viewer` as the client starter when the user needs a publishable frontend repo
- treat AgentMaurice as two backend runtimes: `mode=recipe` and `mode=app`
- prefer `mode=app` plus OpenUI when the user describes an application, dashboard, or interactive operator surface
- treat OpenUI as an optional presentation layer over the mini-app runtime, not as the runtime source of truth
- use governed prepare/apply flows for changes
- present plans before apply
- prefer meta-recette workflows for user-intent changes
- run lightweight verification flows before deep mutations when the user asks for runtime confidence
- ask only blocking questions, and infer the rest conservatively

## Quick Start

1. Install the skill folder from [`skill/agentmaurice`](./skill/agentmaurice) into your assistant's skills directory.
2. Make sure your environment has either:
   - a working AgentMaurice MCP connection
   - or a working `maurice` CLI configuration from [agentmaurice/mauricecli](https://github.com/agentmaurice/mauricecli)
3. If your repository describes an app, create or fill [`templates/agentmaurice.app.md`](./templates/agentmaurice.app.md).
4. If the app also needs a publishable frontend, describe that separately in the `Frontend Strategy` section of the manifest.
5. Start with one of the examples in [`examples`](./examples).

## First Prompt

After installing the skill, a good first prompt is:

```text
Use $agentmaurice to read this repository and build the application described here.
If `agentmaurice.app.md` exists, use it as the source of truth.
Treat the app as one or more deployments with one or more meta-recette blueprint slices.
Ask only blocking questions.
Preview before apply when a mini-app is involved.
If a public frontend is needed, propose a client repo plan based on `agent-maurice-viewer`.
```

## Recommended First Workflows

- Diagnose a deployment:
  [`examples/diagnose-deployment.md`](./examples/diagnose-deployment.md)
- Create an application manifest:
  [`templates/agentmaurice.app.md`](./templates/agentmaurice.app.md)
- Learn the manifest format:
  [`docs/agentmaurice-app-format.md`](./docs/agentmaurice-app-format.md)
- Choose a public client starter:
  [`examples/use-viewer-demo-as-client-app.md`](./examples/use-viewer-demo-as-client-app.md)
- Plan an embedded frontend integration:
  [`examples/use-viewer-embed-in-existing-site.md`](./examples/use-viewer-embed-in-existing-site.md)
- Turn an app idea into a mini-app:
  [`examples/from-idea-to-mini-app.md`](./examples/from-idea-to-mini-app.md)
- Turn an automation idea into a workflow backend:
  [`examples/from-idea-to-workflow-backend.md`](./examples/from-idea-to-workflow-backend.md)
- Build from an application description directory:
  [`examples/from-app-description-directory.md`](./examples/from-app-description-directory.md)
- Describe Firebase or Supabase end-user auth:
  [`examples/firebase-end-user-auth.md`](./examples/firebase-end-user-auth.md),
  [`examples/supabase-end-user-auth.md`](./examples/supabase-end-user-auth.md)
- Preview, verify, and deploy an app:
  [`examples/preview-verify-deploy-app.md`](./examples/preview-verify-deploy-app.md)
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
│   ├── agentmaurice-app-format.md
│   └── install.md
├── templates/
│   └── agentmaurice.app.md
├── examples/
│   ├── create-or-update-recipe.md
│   ├── diagnose-deployment.md
│   ├── firebase-end-user-auth.md
│   ├── from-app-description-directory.md
│   ├── from-idea-to-mini-app.md
│   ├── from-idea-to-workflow-backend.md
│   ├── governed-meta-recette-change.md
│   ├── preview-verify-deploy-app.md
│   ├── supabase-end-user-auth.md
│   ├── use-viewer-demo-as-client-app.md
│   ├── use-viewer-embed-in-existing-site.md
│   ├── verify-mini-app-openui-backend.md
│   └── verify-recipe-backend.md
└── skill/
    └── agentmaurice/
        ├── SKILL.md
        ├── agents/
        │   └── openai.yaml
        └── references/
            ├── app-builder.md
            ├── app-delivery.md
            ├── app-intake.md
            ├── application-model.md
            ├── backend-verification.md
            ├── client-app-repo.md
            ├── end-user-auth.md
            ├── frontend-starter.md
            ├── commands.md
            ├── mcp-tools.md
            └── workflows.md
```

## Notes

- The skill content is intentionally concise.
- Detailed operational material lives in the reference files.
- The examples are repository documentation, not part of the skill payload itself.
- `agentmaurice.app.md` is the canonical application-description entry point for AI-driven builds.
- `agent-maurice-viewer` should be treated as a candidate public client starter, not just as an internal demo.
- The client repo plan should be modeled separately from the AgentMaurice backend topology, even when both are built from the same user idea.
