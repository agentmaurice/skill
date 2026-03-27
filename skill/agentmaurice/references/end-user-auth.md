# AgentMaurice End-User Authentication

Use this reference when the application serves end users through AgentMaurice surfaces and must authenticate them with Firebase, Supabase, or another OIDC provider.

## 1. Product model

Describe end-user auth per deployment.

Why:
- one deployment may expose a viewer for operators
- another deployment may expose only backend recipe execution
- they may not share the same identity provider or mapping strategy

## 2. Code-aligned model

The codebase supports two related layers:
- server auth providers such as Firebase, Supabase, OIDC, Ory, and dev
- deployment-scoped auth connectors for external surfaces

For the application manifest, the useful level is the deployment-scoped auth connector.

## 3. What to describe in `agentmaurice.app.md`

For each deployment that serves end users, capture:
- `provider`
- `auth_mode`
- `auth_connector`
- `mapping`
- `security`

Example shape:

```yaml
deployment: support-console
provider: firebase
auth_mode: bearer_jwt
auth_connector:
  schema: agentmaurice/auth-connector/v1
  mode: gateway
  oidc:
    issuer: https://securetoken.google.com/my-project
    jwks_url: https://www.googleapis.com/service_accounts/v1/jwk/securetoken@system.gserviceaccount.com
    audience:
      - my-project
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
      deployment_id: dep_support_console
  security:
    require_https: true
    enforce_audience: true
    enforce_issuer: true
```

## 4. Provider guidance

Firebase:
- issuer usually looks like `https://securetoken.google.com/<project_id>`
- audience is usually the Firebase project id

Supabase:
- issuer usually looks like `https://<project_ref>.supabase.co/auth/v1`
- audience often defaults to `authenticated`

Generic OIDC:
- use when the user is not on Firebase or Supabase
- still describe issuer, JWKS, audience, claim mapping, and security rules

## 5. Surface guidance

Current code-aligned guidance:
- viewer bootstrap can use bearer JWT when the deployment auth connector is configured
- recipe backend routes can use bearer JWT through dual auth
- mini-app instance routes may still require deployment API keys depending on the current surface

So the skill should not promise uniform bearer-token support everywhere.

## 6. What the skill should do

When the manifest contains end-user auth:
1. include auth setup in the application map
2. keep auth deployment-scoped
3. verify that the chosen surface matches the declared auth mode
4. call out any mismatch between desired UX and current product surface
