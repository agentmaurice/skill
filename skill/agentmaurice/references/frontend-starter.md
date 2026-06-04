# AgentMaurice Frontend Starter

Use this reference when the application needs a real client frontend and the AI should choose a starter instead of inventing one from scratch.

Treat the frontend as a potentially publishable client repository, not only as a local demo.

## Recommended starter repository

Treat `agent-maurice-viewer` as a candidate public starter repository for client applications that consume AgentMaurice mini-app and viewer surfaces.

## Package selection

Use:
- `viewer-demo` when the user wants a full runnable starter app
- `viewer-web` when the user already has a React app and wants a viewer integration
- `viewer-embed` when the user wants a web component that can be embedded in an existing site
- `viewer-core` only for advanced custom integrations

When the user wants a GitHub-ready starter:
- prefer `viewer-demo` for a branded standalone client app
- prefer `viewer-embed` for an existing public site that only needs an integration slice

## Why this matters

The viewer repo already contains:
- bootstrap by `slug` or `deploymentId`
- bootstrap by `applicationKey`, `moduleKey`, and `appKey` for modular
  Applications
- runtime state handling
- event dispatch
- auth adapter support
- separate `X-API-Key` Application/runtime key handling and
  `Authorization: Bearer ...` end-user auth handling
- a Supabase example
- an embeddable web component path

So the skill should prefer it over generating a frontend client stack from scratch.

The skill should also describe:
- whether the starter should become a separate client application repository
- which package is the right publication base
- what branding and auth integration remain to be implemented

## Current caution

The starter is strong for viewer-centric client apps, but the skill should still check whether the target runtime surfaces match the desired auth mode and API access pattern.

In particular:
- legacy viewer bootstrap works with `slug` or `deploymentId`
- modular Application bootstrap uses `applicationKey`, `moduleKey`, `appKey`,
  and an Application/runtime API key
- viewer bootstrap works well with bearer-token end-user flows
- recipe backend verification can also align well
- some mini-app runtime endpoints may still require deployment API keys depending on the current product surface

React modular Application example:

```tsx
<AgentMauriceViewer
  apiBaseUrl="https://api.example"
  apiKey="runtime_application_key"
  applicationKey="salon"
  moduleKey="booking"
  appKey="booking_widget"
  authAdapter={clientAuthAdapter}
/>
```

Web Component modular Application example:

```html
<agent-maurice-viewer
  api-url="https://api.example"
  api-key="runtime_application_key"
  application-key="salon"
  module-key="booking"
  app-key="booking_widget"
  auth-token="end_user_bearer_token"
></agent-maurice-viewer>
```
