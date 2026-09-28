# Application delivery and runtime consumption

Load this reference after architecture/Agent Spec apply when the outcome is a
delivered **Application**, or when an agent must **consume** a published
`public_surface` from outside the authoring rail.

## After apply — delivery report

Report:

- what was built and for which Agent and environment;
- the applied `plan_id`, resource revisions, and source commit;
- Workflows, MiniApps, and Modules created, changed, preserved, or removed;
- end-user authentication and credential-reference assumptions;
- automatic tests and runtime/provenance verification;
- how an authorized caller opens the MiniApp or invokes the Workflow;
- remaining gaps, drift, or manual operational steps.

For a MiniApp, identify the Workflow used for each business side effect and
the verified viewer/bootstrap surface. For a Workflow, identify its public
invocation capability and observed result. For Modules, report catalog
identity, version, source URL, resolved commit, content hash, contributed
resources, and verification results.

Never report success solely because apply returned. Require `spec verify` to
match desired state, observed state, provenance, and blocking tests. If apply
partially committed before a test failure, say so explicitly and report the
current revisions and recovery plan.

## Consume a published Application surface

An Application is the external product boundary: members + semver
`public_surface` + machine keys `sk_maurice_app_…`. Callers never resolve an
Agent outside the published allowlist.

### Create and use an Application API key

Authoring (Bearer / org session):

```text
maurice app key create <applicationId> --name <label> [--scopes surface.read,surface.execute,chat.session] [--expires-at RFC3339]
maurice app key list <applicationId>
maurice app key revoke <applicationId> <keyId>
```

Runtime auth for `/api/v2/applications/…`:

- HTTP header: `X-API-Key: sk_maurice_app_…`
- CLI: `--app-key` / `-K`, or env `MAURICE_APP_KEY`
- Fallback for local admin/dev: session Bearer (no exchange of the app key)

Never log or echo the raw key. Prefer least privilege scopes; default create
scopes usually include `surface.read`, `surface.execute`, and chat/viewer
session scopes when enabled by the server.

### HTTP runtime routes

Base path (client API root already includes `/api`):

```text
GET  /api/v2/applications/{applicationKey}/surface
GET  /api/v2/applications/{applicationKey}/surface/capabilities
POST /api/v2/applications/{applicationKey}/capabilities/{capability}/invoke
POST /api/v2/applications/{applicationKey}/workflows/{workflowId}/executions
POST /api/v2/applications/{applicationKey}/chat/sessions
POST /api/v2/applications/{applicationKey}/chat/sessions/{sessionId}/open
POST /api/v2/applications/{applicationKey}/chat/sessions/{sessionId}/messages
```

Stable refusal codes include `surface_capability_not_exposed`,
`surface_workflow_not_exposed`, and `chat_entrypoint_not_configured`.
Chat requires a published `entrypoints.chat` agent that is an Application
member.

### MauriceCLI runtime commands

```text
maurice app surface get <applicationKey> [--app-key sk_maurice_app_…] [--json]
maurice app capabilities <applicationKey> [--app-key …] [--json]
maurice app invoke <applicationKey> <capability> --input '<json>' [--app-key …] [--json]
maurice app workflow run <applicationKey> <workflowId> --input '<json>' [--app-key …] [--json]
maurice app chat <applicationKey> --message "…" [--session <id>] [--app-key …] [--json]
```

To present a published MiniApp through the durable local One Viewer, create a
contextual display request. Keep the key stable across retries; change it for a
different business operation. The context is non-sensitive correlation only.

```text
maurice app display open <applicationKey> --agent <agentId> --miniapp <miniAppId> \
  --idempotency-key <operationId> --interaction informative|result \
  --context '{"operation_id":"…","reason":"…"}' [--open-browser]
maurice app display show <applicationKey> <requestId>
maurice app display reopen <applicationKey> <requestId> [--open-browser]
maurice app display llm-access <applicationKey> --idempotency-key <operationId> \
  --context '{"reason":"…","feature":"…"}' [--open-browser]
maurice app display action <applicationKey> <actionId> [--open-browser]
```

Use `--instance` on `display open` only to resume an explicitly known instance.
Never place a secret, token, API key, password, authorization header, or full
transcript in `--context`; the server rejects sensitive field names. Secret,
OAuth, and approval interactions remain `maurice action` requests rendered by
the same Viewer under their own `human_action/v1` contract.

Authoring companions (org session, not app key):

```text
maurice app scaffold <key> --kind test|standard --dir <path>
maurice app validate --file <path>/application.yaml
maurice app init <key> --kind test|standard --name "<name>"
maurice app docs <applicationId>
maurice app surface set|publish
maurice app run-config set
maurice app members …
```

Then architecture observe/plan as needed.

Prefer these CLI entrypoints over inventing Workspace Control or V1 miniapp
routes — those rails are removed.

## Debug a MiniApp before you report success

You can create an Agent with `maurice spec init`, author its Workflows and MiniApp, deploy them with `maurice spec deploy`, and launch them yourself. Do that loop. A green `spec verify` or `maurice doctor` is not the page.

1. When an Application already exists, publish its surface (`maurice app surface set`, then `maurice app surface publish`) so the home serves the revision you just deployed.
2. Run `maurice home --no-open --wait 2m`. Open the printed local URL in the browser you can drive before it expires. The URL contains no credential. Click Ouvrir on the Application.
3. Exercise every control the page shows: forms, refresh, row selection, and any other button. Also run `maurice app workflow run` for each Workflow you added.
4. Read the visible error and the HTTP status. A success from `maurice viewer` or `spec verify` does not replace this page. The page opened from the home is the proof.
5. If a control is missing or an action fails, change the spec, commit, deploy, publish, and repeat from step 2.
6. Report the page you saw. Do not call the MiniApp done while a visible action fails or a requested action has no control.
