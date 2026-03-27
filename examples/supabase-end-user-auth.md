# Supabase End-User Authentication

Use this when the application's end users sign in with Supabase and the deployment should trust Supabase bearer tokens on supported AgentMaurice surfaces.

## Prompt

```text
Use $agentmaurice to build this application from its manifest.
Read the deployment auth requirements and treat Supabase as the end-user identity provider.
Explain which AgentMaurice surfaces can use bearer JWT directly and which still need API keys.
```

## Example manifest fragment

~~~md
# End User Authentication

## ops-console auth

```yaml
deployment: ops-console
provider: supabase
auth_mode: bearer_jwt
auth_connector:
  schema: agentmaurice/auth-connector/v1
  mode: gateway
  oidc:
    issuer: https://my-project.supabase.co/auth/v1
    jwks_url: https://my-project.supabase.co/auth/v1/.well-known/jwks.json
    audience:
      - authenticated
    algorithms:
      - RS256
      - ES256
  claims:
    user_id: sub
    email: email
    roles:
      - app_metadata.roles
      - role
  mapping:
    tenant_strategy: static
    static:
      organization_id: org_xxx
      deployment_id: dep_ops_console
  security:
    require_https: true
    enforce_audience: true
    enforce_issuer: true
```
~~~
