# Firebase End-User Authentication

Use this when the application's end users sign in with Firebase and the deployment should trust Firebase bearer tokens on supported AgentMaurice surfaces.

## Prompt

```text
Use $agentmaurice to build this application from its manifest.
Read the deployment auth requirements and treat Firebase as the end-user identity provider.
Model auth per deployment, not only once for the whole app.
Call out any runtime surfaces that still require API keys instead of bearer JWT.
```

## Example manifest fragment

~~~md
# End User Authentication

## support-console auth

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
~~~
