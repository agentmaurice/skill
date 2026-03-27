# Client App Repository Model

Use this reference when the user wants a publishable frontend repository in addition to the AgentMaurice backend application.

## Separate the two artifacts

Do not collapse these into one thing:
- the AgentMaurice backend application
- the public client frontend repository

Use this split:
- `agentmaurice.app.md`: describes the backend product topology inside AgentMaurice
- client app repo plan: describes the public frontend starter, branding, integration mode, and publication strategy

## What the skill should do

When the user wants a real frontend:
1. model the AgentMaurice backend application
2. model the frontend starter choice
3. describe how the frontend connects to the relevant deployment
4. describe auth expectations
5. describe whether the starter should be forked, embedded, or integrated into an existing app
6. describe whether the repo is intended to be public, internal, or temporary

## Good frontend strategy fields

Use these in `agentmaurice.app.md`:
- `starter_project`
- `starter_package`
- `frontend_mode`
- `viewer_entry`
- `target_deployment`
- `auth_adapter`
- `publish_strategy`
- `repo_strategy`
- `branding_scope`

## Publish strategy examples

- `fork_and_brand`
- `embed_in_existing_site`
- `integrate_into_existing_react_app`
- `custom_build_on_viewer_core`

## Repo strategy examples

- `public_github_starter`
- `internal_repo_integration`
- `private_customer_project`
