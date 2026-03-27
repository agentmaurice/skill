# Use `viewer-demo` as a Client App Starter

Use this when the user wants a publishable client frontend and needs a runnable starting point.

## Prompt

```text
Use $agentmaurice to plan this application as two artifacts:
1. the AgentMaurice backend application
2. a public client app based on `agent-maurice-viewer`

For the client frontend, prefer `viewer-demo` as the starter package.
Explain how it should connect to the target deployment, what auth adapter it needs,
and whether it should be forked and branded as a public app.
```

## Expected outcome

- backend application map
- chosen deployment for the client app
- `Frontend Strategy` pointing to `agent-maurice-viewer` + `viewer-demo`
- auth expectations for the viewer bootstrap path
- next implementation steps for branding and publication
