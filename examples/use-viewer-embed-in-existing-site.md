# Use `viewer-embed` in an Existing Site

Use this when the user already has a website or application and wants to embed AgentMaurice viewer functionality instead of starting a whole new frontend app.

## Prompt

```text
Use $agentmaurice to plan this application as an AgentMaurice backend plus an embedded client integration.
For the frontend, prefer `agent-maurice-viewer` with the `viewer-embed` package.
Explain which deployment it should target, how auth should be handled,
and whether the current runtime surface is compatible with the desired user flow.
```

## Expected outcome

- backend application map
- target deployment for the embed
- `Frontend Strategy` pointing to `agent-maurice-viewer` + `viewer-embed`
- auth and access surface notes
- next steps for integrating the web component in the existing site
