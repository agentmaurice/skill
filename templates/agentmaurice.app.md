---
app_id: example-support-ops
name: Example Support Operations App
version: 0.1
default_strategy: slice_by_slice
preferred_ui_runtime: openui
default_deployment_mode: standard
---

# Product Intent

Describe the application from the user's point of view.
Explain what problem it solves and what outcome matters most.

# Users

- Primary user:
- Secondary user:

# Deployments

| id | purpose | exposure | notes |
|---|---|---|---|
| app-console | Interactive app surface | viewer | Main operator UI |
| app-automation | Workflow backend | api | Background or triggered processing |

# Blueprint Slices

## console

```yaml
type: meta_recette
runtime: app
deployment: app-console
ui_runtime: openui
```

Goal:
Describe the interactive slice this blueprint should deliver.

Inputs:
- input 1
- input 2

Actions:
- action 1
- action 2

Acceptance:
- the user can complete the main task
- preview works before apply
- runtime access is testable after deploy

## automation

```yaml
type: meta_recette
runtime: recipe
deployment: app-automation
```

Goal:
Describe the backend or workflow slice this blueprint should deliver.

Inputs:
- input 1
- input 2

Outputs:
- output 1
- output 2

Acceptance:
- the backend returns the expected result shape
- execution status is observable

# Integrations

- integration 1
- integration 2

# End User Authentication

Describe how end users of this application authenticate to the external AgentMaurice surfaces.

## app-console auth

```yaml
deployment: app-console
provider: firebase
auth_mode: bearer_jwt
auth_connector:
  schema: agentmaurice/auth-connector/v1
  mode: gateway
  oidc:
    issuer: https://securetoken.google.com/YOUR_FIREBASE_PROJECT_ID
    jwks_url: https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com
    audience:
      - YOUR_FIREBASE_PROJECT_ID
    algorithms:
      - RS256
  claims:
    user_id: sub
    email: email
    roles:
      - roles
      - permissions
    tenant:
      - tenant
  mapping:
    tenant_strategy: static
    static:
      organization_id: org_xxx
      deployment_id: dep_app_console
  security:
    require_https: true
    enforce_audience: true
    enforce_issuer: true
```

Notes:
- viewer and recipe backend surfaces can use bearer JWT when the deployment auth connector is configured
- mini-app instance endpoints may still require deployment API keys depending on the current runtime surface

# Frontend Strategy

Describe how the client application should be built and whether it should start from `agent-maurice-viewer`.

```yaml
starter_project: agent-maurice-viewer
starter_package: viewer-demo
frontend_mode: react_app
viewer_entry: slug
target_deployment: app-console
auth_adapter: firebase
publish_strategy: fork_and_brand
repo_strategy: public_github_starter
branding_scope: customer_facing_app
```

Goals:
- ship a usable client frontend quickly
- reuse AgentMaurice viewer bootstrap and runtime rendering
- avoid rebuilding the client runtime from scratch

Notes:
- use `viewer-demo` for a full starter app
- use `viewer-web` for a React integration inside a custom app
- use `viewer-embed` for an embeddable web component
- use `viewer-core` only for advanced custom integrations

# Access Surfaces

- viewer bootstrap for the interactive deployment
- recipe execution endpoint for the backend deployment

# Verification

- preview the mini-app before apply
- verify viewer bootstrap or app runtime after deploy
- execute one backend workflow after deploy

# Rollout Order

1. console
2. automation

# Open Questions

- unresolved point 1
- unresolved point 2
