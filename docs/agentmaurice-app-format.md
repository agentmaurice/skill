# `agentmaurice.app.md` Format V1

This repository uses `agentmaurice.app.md` as the canonical user-facing application description file.

The file is meant to describe an application as a user sees it, not as AgentMaurice stores it internally.

## Purpose

An AI using the AgentMaurice skill should be able to read this file and infer:
- the application boundary
- the deployment topology
- the blueprint slices
- the runtime mode for each slice
- the verification strategy
- the rollout order

## Canonical filename

Use:

```text
agentmaurice.app.md
```

If a repository has a richer application description directory, this file should stay the main entry point and link to the rest.

## Recommended location

Use one of these:
- repository root: `agentmaurice.app.md`
- application folder root: `<app-directory>/agentmaurice.app.md`

## Required sections

- `Product Intent`
- `Deployments`
- `Blueprint Slices`
- `Integrations`
- `Verification`

## Recommended sections

- `Users`
- `Access Surfaces`
- `End User Authentication`
- `Frontend Strategy`
- `Rollout Order`
- `Open Questions`
- `Constraints`
- `Non Goals`

## Parsing rules for the skill

The skill should:
1. Look for `agentmaurice.app.md` first.
2. Read it before asking clarifying questions.
3. Treat the application as one or more deployments with one or more meta-recette blueprint slices.
4. Map each blueprint slice to `mode=app` or `mode=recipe`.
5. If `End User Authentication` is present, model authentication per deployment.
6. If `Frontend Strategy` is present, model the client application separately from the AgentMaurice backend.
7. Build slice by slice when the application is too large for a single safe change.

The skill should not:
- assume one application equals one meta-recette
- assume one application equals one deployment
- assume every slice is interactive

## End-user authentication note

Describe end-user auth per deployment, not only once for the whole application.

Good fields to include:
- provider: `firebase`, `supabase`, or generic `oidc`
- auth mode: `bearer_jwt`, `api_key`, or `bearer_or_api_key`
- auth connector configuration
- tenant or deployment mapping strategy

Current runtime nuance:
- viewer bootstrap and recipe backend surfaces can use bearer JWT when a deployment auth connector is configured
- some mini-app runtime endpoints may still remain API-key-only depending on the current product surface

## Frontend strategy note

Use `Frontend Strategy` to describe the public client application.

Good fields to include:
- `starter_project`
- `starter_package`
- `frontend_mode`
- `viewer_entry`
- `target_deployment`
- `auth_adapter`
- `publish_strategy`
- `repo_strategy`
- `branding_scope`

Recommended values:
- `starter_project: agent-maurice-viewer`
- `starter_package: viewer-demo | viewer-web | viewer-embed | viewer-core`
- `repo_strategy: public_github_starter | internal_repo_integration`

Important modeling rule:
- the AgentMaurice application manifest describes the backend product topology
- the frontend strategy describes the client app repo that consumes it

## Official V1 template

See:
- [`templates/agentmaurice.app.md`](../templates/agentmaurice.app.md)
