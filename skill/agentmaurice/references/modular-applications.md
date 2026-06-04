# AgentMaurice Modular Applications

Use this reference when the user wants an AgentMaurice `Application` composed
of modules, or when they ask the agent to create, validate, publish, import, or
install modules.

## 1. When to use this workflow

Use modular Applications for:
- reusable business capabilities such as booking, users, click and collect, or
  online shop modules
- several independently developed modules assembled into one product
- organization-private modules stored in private Git repositories
- repeated installation of the same functional module for several customers

Do not use this workflow just because the user says "app". If the user wants a
single one-off mini-app or workflow backend, the governed Agent Spec workflow
may be enough.

## 2. Runtime model

Keep these objects distinct:
- `Application`: organization runtime resource composed of modules
- module: installable package with `agentmaurice.module/v1`
- Module Catalog entry: imported module manifest plus source URL, ref, resolved
  commit SHA, module hash, version, visibility, and status
- module installation: desired or installed module inside one Application
- application/module binding: link from Application and module key to the
  target deployment

One installed module maps to one AgentMaurice deployment. That deployment still
has one canonical Agent Spec/meta-recette in V1.

The runtime is generic:

```text
GET      /applications/{applicationKey}/modules
GET      /applications/{applicationKey}/modules/{moduleKey}/capabilities
POST     /applications/{applicationKey}/modules/{moduleKey}/actions/{actionKey}
GET|POST /applications/{applicationKey}/modules/{moduleKey}/queries/{queryKey}
POST     /applications/{applicationKey}/modules/{moduleKey}/apps/{appKey}/sessions
POST     /applications/{applicationKey}/modules/{moduleKey}/apps/{appKey}/events
```

Do not invent business-specific backend routes for modules. The module manifest
declares capabilities; AgentMaurice resolves the route dynamically.

## 3. Start with discovery

Before creating or installing modules, inspect the current contract:

```text
inception_call(tool_name="inception_deployment_doctor", arguments={"format":"ai_contract"})
inception_call(tool_name="inception_mcp_capabilities", arguments={})
```

Confirm:
- `capabilities.modular_applications=true`
- `capabilities.module_catalog=true`
- `capabilities.application_runtime=true`
- `modular_applications.status=implemented`
- `modular_applications.application_kinds` contains `standard` and `test`
- schemas include `agentmaurice.module/v1`,
  `agentmaurice.application/v1`, and `agentmaurice.module-catalog/v1`

In V1, External Inception documents this surface but does not mutate it
directly. Use MauriceCLI or the HTTP API for catalog and Application
management.

## 4. Author a module

Scaffold a module:

```bash
maurice module init booking --dir booking-module
cd booking-module
```

Expected files:
- `module.yaml`
- `deployments/main/agent-spec.json`
- `deployments/main/recipes/*.json`
- `deployments/main/tests/test-plan.json`

Validate locally:

```bash
maurice module validate --file module.yaml
maurice module test --file module.yaml
```

The manifest must declare:
- `schema_version: agentmaurice.module/v1`
- stable module `key`
- semantic `version`
- deployment alias and Agent Spec path
- provided capabilities: `actions`, `queries`, and/or `apps`
- required MCPs, docs, memory, config, and capabilities when needed

Do not put secrets in the manifest. Config defaults must be non-secret.

## 5. Import or publish a module

Public or organization-visible Git module:

```bash
maurice catalog modules import \
  https://github.com/example/agentmaurice-booking-module.git \
  --ref main \
  --visibility organization \
  --tags booking,appointments \
  --json
```

Publish from the current Git repo:

```bash
maurice module publish \
  --ref main \
  --visibility organization \
  --tags booking,appointments \
  --json
```

The import/publish result must include enough lock context for review:
- source URL
- requested ref
- resolved commit SHA
- module hash
- declared version
- module key
- catalog entry ID

If the resolved commit SHA or module hash is missing in a production-like
context, stop and do not install.

## 6. Test Application and viewer preview

A module developer should test modules inside a real `Application` before
publishing them. Use `kind=test` for this sandbox. It is not a separate
runtime; it is a normal Application whose CLI defaults are optimized for
development.

```bash
maurice app init booking-dev --kind test --name "Booking Dev" --json
maurice app add booking-dev . --dev --json
maurice app add booking-dev users --json
maurice app plan booking-dev --out app-plan.json --json
maurice app apply booking-dev --plan app-plan.json --plan-hash <hash> --tests auto --json
maurice app status booking-dev --json
maurice app docs booking-dev
```

For `maurice app add . --dev`:
- the local module manifest must validate
- the local Git repo must be clean
- the current commit must be reachable from the configured remote
- the CLI imports an organization catalog entry tagged `dev`, then adds it to
  the Application
- only credential IDs may be referenced; raw Git secrets must never be written
  into manifests, docs, locks, logs or answers

Preview a declared mini-app capability with `agent-maurice-viewer`:

```tsx
<AgentMauriceViewer
  apiBaseUrl="https://api.example"
  apiKey="runtime_application_key"
  applicationKey="booking-dev"
  moduleKey="booking"
  appKey="booking_widget"
  authAdapter={clientAuthAdapter}
/>
```

Web Component:

```html
<agent-maurice-viewer
  api-url="https://api.example"
  api-key="runtime_application_key"
  application-key="booking-dev"
  module-key="booking"
  app-key="booking_widget"
  auth-token="end_user_bearer_token"
></agent-maurice-viewer>
```

Viewer rules:
- `X-API-Key` carries the Application/runtime API key
- `Authorization: Bearer ...` carries the end-user token
- the viewer calls only the generic Application runtime endpoints:
  capabilities, app sessions, and app events
- the viewer adapts `{instance, ui, effects}` into the existing viewer runtime
  payload

## 7. Private Git modules

Create a credential reference:

```bash
maurice git credential create company-modules \
  --provider github \
  --auth-type https_token \
  --secret-file .git-token
```

Test it:

```bash
maurice git credential test <credential_id> --url <private-git-url> --json
```

Import with the credential reference:

```bash
maurice catalog modules import \
  <private-git-url> \
  --ref main \
  --credential <credential_id> \
  --visibility organization \
  --json
```

Security rules:
- never put the token or private key in `module.yaml`
- never echo secret values in final answers
- avoid passing secrets on the command line when possible; use
  `--secret-file`, environment injection, or the platform secret store
- only store credential IDs or names in local notes

## 8. Compose a client Application

Create or inspect:

```bash
maurice app list --json
maurice app init salon --kind standard --name "Salon Application" --json
maurice app get salon --json
```

Add modules:

```bash
maurice app add salon users --json
maurice app add salon booking --version 0.1.0 --json
maurice app add salon https://git.example/modules/booking.git --ref v0.1.0 --json
```

If the module needs non-secret overrides:

```bash
maurice app add salon booking \
  --config-overrides booking-overrides.json \
  --json
```

Never put secrets in `booking-overrides.json`.

## 9. Plan, approval, apply

Plan:

```bash
maurice app plan salon --out app-plan.json --json
```

Review the plan before apply:
- `plan_hash`
- install/update/remove actions
- module key and version
- source URL
- requested ref
- resolved commit SHA
- module hash
- target deployment ID or deployment creation action
- MCP installation actions
- recipe/mini-app/capability changes

Ask the user for explicit approval containing the exact `plan_hash`.

Apply:

```bash
maurice app apply salon \
  --plan app-plan.json \
  --plan-hash <hash> \
  --tests auto \
  --json
```

`--tests auto` runs tests by default for `kind=test` Applications and skips
them by default for `kind=standard`. `--run-tests` remains a backward-compatible
alias for `--tests on`.

If apply fails because the module hash no longer matches the lock, stop. Do
not force apply. Re-import or sync the catalog entry, then plan again.

## 10. Status and runtime verification

Inspect:

```bash
maurice app status salon --json
maurice app docs salon
```

Verify at least one declared capability:
- list modules
- list module capabilities
- call one safe query or action, or create one mini-app session
- check the target deployment Doctor when a module install changed deployment
  state

Use the generic runtime endpoints from Doctor/capabilities. Do not invent
module-specific endpoints.

## 11. Final handoff

When done, report:
- Application key and name
- installed module keys and versions
- catalog entry IDs and source refs
- resolved commit SHAs and module hashes
- target deployments created or updated
- capabilities exposed by each module
- auth assumptions, especially deployment-scoped end-user auth
- what was verified
- remaining gaps, if any

Keep secrets out of the handoff.
