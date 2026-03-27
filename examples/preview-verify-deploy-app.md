# Preview, Verify, and Deploy an App

Use this when the user already has an application intent and wants a disciplined path to deployment.

## Prompt

```text
Use $agentmaurice to prepare this application, preview it, verify the runtime surface,
and deploy it only after showing me the plan.
If it is interactive, treat it as a mini-app with OpenUI delivery and native fallback.
After deploy, return the access path and the verification summary.
The app idea is:
"An operations cockpit for reviewing customer onboarding cases."
```

## Expected Flow

```text
1. Bootstrap workspace and Doctor
2. Prepare the governed change from user intent
3. Preview the mini-app if applicable
4. Verify viewer/runtime or backend execution path
5. Present the plan
6. Apply
7. Re-check final state
8. Return the delivered app summary
```
