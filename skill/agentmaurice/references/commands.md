# Maurice CLI — Current Command Guide

Use the CLI in three different ways:
- `maurice agent connect` to connect a coding agent and initialize the local
  AgentMaurice project.
- `maurice env ...` and `maurice spec ...` for Git-native Agent Spec work.
- `maurice catalog modules ...`, `maurice module ...`, `maurice app ...`, and
  `maurice git credential ...` for modular Applications.
- `maurice workspace ...` or `maurice tools ...` for legacy or low-level
  operational flows.

For a developer using Claude Code, Codex, Cursor, Windsurf, or another coding
agent, prefer `maurice agent connect` when an `amc_...` bootstrap command is
available from AgentMaurice OS.

## 1. Bootstrap and Connectivity

Check connectivity:

```bash
maurice ping --json
maurice whoami --json
```

Config file:
- `$HOME/.maurice/config.yaml`

Project files:
- `agentmaurice.yaml`
- `agentmaurice.lock.json`
- `environments/<env>.yaml`
- `deployments/<alias>/agent-spec.json`
- `deployments/<alias>/recipes/*.json`
- `deployments/<alias>/tests/test-plan.json`

Secrets are stored only in the local CLI config. They must never be written
into the project repository.

Module manifests and Application files must also stay non-secret. Private Git
sources use credential references, not raw tokens or SSH private keys.

## 2. Connect a Coding Agent

AgentMaurice OS can generate a single command:

```bash
maurice agent connect "<cli-bootstrap-url>" \
  --client claude-code \
  --env dev \
  --deployment-alias support \
  --dir .
```

Supported client values:
- `claude-code`
- `codex`
- `cursor`
- `windsurf`
- `generic`

Behavior:
- consumes the `amc_...` CLI bootstrap once
- stores local credentials for the selected environment
- writes non-secret Git-native project files
- runs `spec pull` by default
- creates and consumes an External Inception bootstrap
- configures the selected MCP client when supported, or prints generic MCP
  setup instructions

Useful flags:

```bash
maurice agent connect "<url>" --client generic --env dev --deployment-alias support --dir .
maurice agent connect "<url>" --client claude-code --env dev --deployment-alias support --dir . --force
maurice agent connect "<url>" --client generic --env dev --deployment-alias support --dir . --no-pull
printf '%s' "<url>" | maurice agent connect --paste --client generic --env dev --deployment-alias support --dir .
```

If automatic client setup fails, keep the initialized project and use the
manual MCP command printed by the CLI.

## 3. Environments

Initialize or inspect environments:

```bash
maurice env init dev \
  --api https://dev.example \
  --organization org_dev \
  --deployment-alias support \
  --deployment dep_dev_support \
  --kind development

maurice env list
maurice env use dev
maurice env show dev
maurice env status --env dev
```

Connect from an AgentMaurice OS bootstrap without configuring a coding-agent
client:

```bash
maurice env connect "<cli-bootstrap-url>" \
  --env dev \
  --deployment-alias support \
  --dir .
```

Default environment resolution:
1. `--env`
2. `current.environment` in `$HOME/.maurice/config.yaml`
3. `agentmaurice.yaml.default_environment`

Never infer `prod`, `preprod`, `dev`, or deployment aliases from display names.
Use the declared environment and alias.

## 4. Git-Native Agent Spec

Pull the deployed Agent Spec into the repository:

```bash
maurice spec pull --env dev --deployment-alias support --dir .
```

Validate local project files:

```bash
maurice spec validate --env dev --deployment-alias support --dir .
```

Plan a change without mutating AgentMaurice:

```bash
maurice spec plan \
  --env dev \
  --deployment-alias support \
  --dir . \
  --out plan.json \
  --json
```

Persist conversation approval:

```bash
maurice spec approve \
  --env dev \
  --plan plan.json \
  --text "I approve dev <plan_hash>"
```

Apply the approved plan:

```bash
maurice spec apply \
  --env dev \
  --plan plan.json \
  --approval-id <approval_id>
```

Check status:

```bash
maurice spec status --env dev --deployment-alias support
```

Rules:
- edit recipe files under `deployments/<alias>/recipes/*.json`
- do not send an incomplete Agent Spec as a replacement
- the complete `recipes_definitions` set is reconstructed from all recipe files
- keep `agentmaurice.lock.json` per environment and deployment alias
- if apply returns `meta_recette_version_conflict`, pull/export again, merge in
  Git, validate, plan, approve and apply again
- protected production environments can require a clean Git workspace, commit
  SHA, PR URL, and approval text containing both the exact `plan_hash` and the
  environment name

## 5. Modular Applications and Modules

Use this workflow when the user asks to create reusable modules, import modules
from Git, or deploy an AgentMaurice `Application` composed of several modules.

Discover the Module Catalog:

```bash
maurice catalog modules list --json
maurice catalog modules search booking --json
maurice catalog modules info booking --json
```

Create or validate a module repo:

```bash
maurice module init booking --dir .
maurice module validate --file module.yaml
maurice module test --file module.yaml
maurice module publish
```

Import a public Git module:

```bash
maurice catalog modules import \
  https://github.com/example/agentmaurice-booking-module.git \
  --ref main \
  --visibility organization \
  --json
```

Import a private Git module:

```bash
maurice git credential create \
  company-modules \
  --provider github \
  --auth-type https_token \
  --secret-file .git-token

maurice git credential list --json
maurice git credential test <credential_id> --url <private-git-url> --json

maurice catalog modules import \
  <private-git-url> \
  --ref main \
  --credential <credential_id> \
  --visibility organization \
  --json
```

Compose an Application:

```bash
maurice app init salon --name "Salon Application" --json
maurice app add salon users --json
maurice app add salon booking --json
maurice app plan salon --out app-plan.json --json
```

Before apply:
- read the plan
- record the exact `plan_hash`
- check module source URL, requested ref, resolved commit SHA, module hash,
  declared version, target deployment, and install/update action
- ask for explicit approval containing the hash

Apply and inspect:

```bash
maurice app apply salon \
  --plan app-plan.json \
  --plan-hash <hash> \
  --json

maurice app status salon --json
maurice app docs salon
```

Security rules:
- do not print raw credential values
- do not put raw Git tokens, SSH keys, API keys, or bearer tokens into module
  manifests, Application files, lock files, logs, prompts, or answers
- in production-like contexts, never install from a moving ref without a
  resolved commit SHA and module hash
- if a hash mismatch is reported, stop and re-import or re-plan; do not force
  install stale content

Runtime verification should use the generic Application routes documented by
Doctor/capabilities. Do not invent module-specific API routes.

## 6. External Inception Through Low-Level Tools

Use this only when the agent has no MCP server configured but has a deployment
API key and must call Inception tools through the CLI.

List tools:

```bash
maurice tools list --deployment <deployment_id>
```

Describe a tool:

```bash
maurice tools describe inception_meta_recette_compile --deployment <deployment_id>
```

Initial discovery:

```bash
maurice tools call inception_deployment_scopes_list --deployment <deployment_id>
maurice tools call inception_deployment_doctor --deployment <deployment_id> --arg format=ai_contract
maurice tools call inception_mcp_capabilities --deployment <deployment_id>
maurice tools call inception_integrations_inventory --deployment <deployment_id>
```

Guided Meta-Recette flow:

```bash
maurice tools call inception_meta_recette_ensure --deployment <deployment_id> --arg target_deployment_id=<deployment_id>
maurice tools call inception_meta_recette_compile --deployment <deployment_id> --arg meta_recette_id=<mrid> --arg dry_run=true
maurice tools call inception_meta_recette_compile --deployment <deployment_id> --arg meta_recette_id=<mrid> --arg dry_run=false
maurice tools call inception_meta_recette_plan_apply --deployment <deployment_id> --arg meta_recette_id=<mrid>
maurice tools call inception_meta_recette_approve_plan --deployment <deployment_id> --arg meta_recette_id=<mrid> --arg plan_id=<plan_id> --arg plan_hash=<hash> --arg approval_text='I approve <hash>'
maurice tools call inception_meta_recette_apply --deployment <deployment_id> --arg meta_recette_id=<mrid> --arg approval_id=<approval_id> --arg approved_plan_hash=<hash>
```

Recipe execution and usage:

```bash
maurice tools call inception_recipe_run_observed --deployment <deployment_id> --arg recipe_id=<recipe_id> --arg logs_limit=50 --arg trace_limit=50
maurice tools call inception_recipe_execution_usage --deployment <deployment_id> --arg execution_id=<execution_id>
```

Direct runtime MCP tool call:

```bash
maurice tools call inception_runtime_tool_call \
  --deployment <deployment_id> \
  --arg tool_name=storage--list_files \
  --arg arguments='{}'
```

## 7. Workspace Control

Use Workspace Control when the user is explicitly operating through a Calisto
workspace or a workspace session.

```bash
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace get
maurice workspace tools list
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_current_state
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='Add a support dashboard'
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```

Prepared-plan lifecycle:

```bash
maurice workspace plan prepare
maurice workspace plan inspect
maurice workspace plan approve --plan-hash <hash> --comment "validated"
maurice workspace plan apply --run-tests=false
maurice workspace plan clear
```

## 8. Internal Exploration

Use `maurice ai run` only when the user explicitly wants autonomous synthesis by
the internal AgentMaurice model, not when you need a deterministic governed
change pipeline.

```bash
maurice ai run \
  --deployment <deployment_id> \
  --prompt "Diagnose this deployment and summarize the main issues." \
  --timeout 120
```

## 9. Practical Rule

For a coding agent in a project repository, the best CLI path is usually:

```bash
maurice agent connect "<cli-bootstrap-url>" --client generic --env dev --deployment-alias support --dir .
maurice spec validate --env dev --deployment-alias support
maurice spec plan --env dev --deployment-alias support --out plan.json --json
maurice spec approve --env dev --plan plan.json --text "I approve dev <plan_hash>"
maurice spec apply --env dev --plan plan.json --approval-id <approval_id>
```

For a non-developer prompt-only connection, use the `amb_...` agent-discovery
URL and then the MCP setup described by the returned discovery contract.
