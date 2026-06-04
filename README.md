# AgentMaurice Skill

Repository for an English-language AgentMaurice skill that helps an AI:
- turn a raw app idea into a deployed AgentMaurice application
- model that application as one or more deployments with one or more meta-recettes
- connect through agent-discovery bootstrap URLs or `maurice agent connect`
- operate Git-native AgentMaurice projects with environments and Agent Specs
- create, import, and install reusable application modules through the Module
  Catalog and modular `Application` runtime
- choose and describe a public client frontend starter when needed
- inspect deployments safely
- configure deployment surfaces through External Inception when a deployment key is available
- run recipes, call visible runtime MCP tools, inspect traces, and compare usage
- use managed web search/fetch/extract tools when external documentation is needed
- operate AgentMaurice as a workflow backend and a mini-app backend
- verify recipe runtimes, viewer bootstrap, and OpenUI-backed mini-app delivery
- use the Workspace Control MCP gateway
- fall back to the `maurice` CLI
- run governed meta-recette and recipe workflows

## What You Can Do With It

Use this skill when you want an AI in Claude Code, Codex, or a similar agentic environment to:
- read an application idea or a repository description
- map that idea to AgentMaurice deployments, Agent Specs, and conceptual slices
- choose whether each slice should be a mini-app or a workflow backend
- describe end-user authentication such as Firebase, Supabase, or generic OIDC
- choose a frontend starter such as `agent-maurice-viewer`
- prepare, preview, verify, and deploy the resulting application
- preserve the canonical Agent Spec while creating or updating recipes
- create module manifests, validate modules, import Git modules, and compose
  modular Applications with a `kind=test` development sandbox, viewer preview,
  publication/import, then `kind=standard` client Applications
- collaborate through Git across dev, preprod, and production environments

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
- [`skill/agentmaurice/references/modular-applications.md`](./skill/agentmaurice/references/modular-applications.md): Module Catalog and modular `Application` workflow

## Who This Is For

Use this skill if you want an AI assistant to operate AgentMaurice through:
- an AgentMaurice OS prompt-only `amb_...` agent-discovery bootstrap
- `maurice agent connect` for a developer Git-native workflow
- the Workspace Control MCP gateway
- the External Inception MCP gateway
- the `maurice` CLI

This repository is aimed at teams who want a portable, publishable skill package
instead of a private skill buried inside a mono-repo.

It is especially useful if you want a user to be able to say:

```text
Here is my app idea. Build it on AgentMaurice, choose the right runtime,
guide me only on blocking questions, and tell me how to access the result.
```

## Core Design

The skill follows a few simple rules:
- Doctor first
- choose the explicit environment and deployment alias before acting
- start from user intent, not from internal implementation nouns
- prefer the agent-discovery contract or `maurice agent connect` for coding agents
- use External Inception `inception_search`/`inception_call` when a code-mode MCP client only exposes meta-tools
- treat a meta-recette as an application blueprint slice, not as the whole application
- distinguish application idea, runtime `Application`, module, Module Catalog
  entry, deployment, Agent Spec, and recipe
- treat one deployment's Agent Spec/meta-recette as the complete source of truth for its recipes
- never drop existing recipes by sending a partial spec replacement
- expect a real application to span one or more deployments and one or more meta-recettes
- use explicit deployment scopes and `target_deployment_alias` for cross-deployment recipe calls
- treat the client frontend repo as a separate public artifact when the user needs a branded application front
- prefer `agent-maurice-viewer` as the client starter when the user needs a publishable frontend repo
- treat AgentMaurice as two backend runtimes: `mode=recipe` and `mode=app`
- prefer `mode=app` plus OpenUI when the user describes an application, dashboard, or interactive operator surface
- treat OpenUI as an optional presentation layer over the mini-app runtime, not as the runtime source of truth
- use governed prepare/apply flows for changes
- use `maurice catalog modules`, `maurice module`, `maurice app`, and
  `maurice git credential` for modular Applications; External Inception only
  discovers this surface in V1
- use `agent-maurice-viewer` with `applicationKey`, `moduleKey`, and `appKey`
  to preview modular Application mini-apps
- in External Inception `guided`, persist explicit chat approval with `inception_meta_recette_approve_plan`
- use `inception_runtime_tool_call` for direct visible runtime MCP tools
- use `inception_recipe_run_observed` and `inception_recipe_execution_usage` for execution, traces and usage
- treat integration runtime tools as deployment-scoped; org-level catalog is only a directory/billing surface
- distinguish `allowed_llm_models` as the effective recipe-callable list, including active hosted AgentMaurice chat models when the hosted provider is active
- use managed web tools only after internal AgentMaurice sources and runtime state, with URL citations
- present plans before apply
- prefer meta-recette workflows for user-intent changes
- run lightweight verification flows before deep mutations when the user asks for runtime confidence
- ask only blocking questions, and infer the rest conservatively

## Quick Start

1. Install the skill folder from [`skill/agentmaurice`](./skill/agentmaurice) into your assistant's skills directory.
2. Make sure your environment has either:
   - a prompt-only AgentMaurice OS bootstrap URL (`amb_...`)
   - a `maurice agent connect ...` command generated by AgentMaurice OS
   - a working AgentMaurice MCP connection
   - or an existing Git-native AgentMaurice project with `agentmaurice.yaml`
3. If you receive an `amb_...` URL, consume it once, read the discovery contract, configure MCP from `client_setup` if possible, then call scopes list, Doctor and capabilities.
4. If you receive a CLI command, run `maurice agent connect ...` and then use
   `maurice spec validate/plan/apply` for Agent Specs, or
   `maurice catalog modules` / `maurice module` / `maurice app` for modular
   Applications.
5. If your repository describes an app, create or fill [`templates/agentmaurice.app.md`](./templates/agentmaurice.app.md).
6. If the app also needs a publishable frontend, describe that separately in the `Frontend Strategy` section of the manifest.
7. Start with one of the examples in [`examples`](./examples).

## First Prompt

After installing the skill, a good first prompt is:

```text
Use $agentmaurice to read this repository and build the application described here.
If `agentmaurice.app.md` exists, use it as the source of truth.
If `agentmaurice.yaml` exists, use the declared environment and deployment aliases.
If `module.yaml` exists, validate it before import or publish.
Treat the app as one or more deployments, each with one canonical Agent Spec.
If the user asks for reusable modules, create a test Application first, preview
declared mini-apps with the viewer, then publish/import modules and compose the
client Application.
Ask only blocking questions.
Preview before apply when a mini-app is involved.
If a public frontend is needed, propose a client repo plan based on `agent-maurice-viewer`.
```

## Recommended First Workflows

- Diagnose a deployment:
  [`examples/diagnose-deployment.md`](./examples/diagnose-deployment.md)
- Connect a code agent and initialize a Git-native project:
  [`skill/agentmaurice/references/workflows.md`](./skill/agentmaurice/references/workflows.md#14-connect-a-code-agent-to-agentmaurice)
- Work in a Git-native AgentMaurice project:
  [`skill/agentmaurice/references/workflows.md`](./skill/agentmaurice/references/workflows.md#11-git-native-agentmaurice-project-workflow)
- Compose a modular Application from modules:
  [`skill/agentmaurice/references/modular-applications.md`](./skill/agentmaurice/references/modular-applications.md)
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
- Run and observe a recipe backend:
  [`examples/verify-recipe-backend.md`](./examples/verify-recipe-backend.md)

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
            ├── modular-applications.md
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
