# Maurice CLI — Current Command Guide

Use the CLI in two different ways:
- `maurice workspace ...` for organization and workspace governed control
- `maurice tools ...` for low-level deployment-scoped tool calls

Prefer `maurice workspace` when reproducing the Workspace Control MCP flows.

## 1. Bootstrap

Check connectivity:
```bash
maurice ping --json
maurice whoami --json
```

Config file:
- `$HOME/.maurice/config.yaml`

If the workspace gateway is not configured yet, issue an orgctrl credential:
```bash
maurice workspace auth issue --organization <org_id>
```

This stores:
- `auth.workspace_api_key`
- `auth.workspace_role`

## 2. Workspace CLI

List available workspace sessions:
```bash
maurice workspace list
```

Bind the current CLI context:
```bash
maurice workspace bind <workspace_session_id>
```

Get current bound state:
```bash
maurice workspace get
```

List the gateway tools exposed to the CLI:
```bash
maurice workspace tools list
```

Call any workspace tool:
```bash
maurice workspace call workspace_bootstrap_contract --arg goal=update_meta_recette
maurice workspace call workspace_current_state
maurice workspace call workspace_feature_prepare --arg goal=update_meta_recette --arg intent_markdown='Add a support dashboard'
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
maurice workspace call workspace_recipe_identity_repair --arg canonical_recipe_id=<recipe_id>
```

Deployment targeting:
```bash
maurice workspace deployments list
maurice workspace target set <deployment_id>
```

Prepared-plan lifecycle:
```bash
maurice workspace plan prepare
maurice workspace plan inspect
maurice workspace plan approve --plan-hash <hash> --comment "validated"
maurice workspace plan apply --run-tests=false
maurice workspace plan clear
```

Reconcile:
```bash
maurice workspace reconcile
```

Capability contracts:
```bash
maurice workspace capabilities exports
maurice workspace capabilities imports
maurice workspace capabilities contract <capability_ref>
maurice workspace capabilities registry search --query auth
maurice workspace capabilities validate-imports
```

## 3. Low-level tool calls

Use these when the user explicitly wants direct deployment-scoped tool calls.

List tools:
```bash
maurice tools list --deployment <id>
```

Describe a tool:
```bash
maurice tools describe inception_meta_recette_compile --deployment <id>
```

Call a tool:
```bash
maurice tools call inception_deployment_doctor --deployment <id> --arg format=ai_contract
maurice tools call inception_meta_recette_list --deployment <id>
maurice tools call inception_meta_recette_compile --deployment <id> --arg meta_recette_id=<mrid>
maurice tools call inception_meta_recette_plan_apply --deployment <id> --arg meta_recette_id=<mrid>
maurice tools call inception_meta_recette_apply --deployment <id> --arg meta_recette_id=<mrid> --arg approved=true --arg approved_plan_hash=<hash>
```

## 4. Naming caution

Current low-level recipe tools are centered on:
- `inception_recipe_definitions_*`
- `inception_recipe_executions_*`

If the brief is business-oriented, prefer the meta-recette workflow instead of raw recipe-definition calls.

## 5. `ai run`

Use this when the user wants delegated exploration by the internal gamemaster:
```bash
maurice ai run \
  --deployment <id> \
  --prompt "Diagnose this deployment and summarize the main issues." \
  --timeout 120
```

## 6. Testing shortcut

Meta-recette roundtrip:
```bash
maurice test meta-roundtrip --target-deployment <id> --bundle /path/to/bundle.json --timeout 180
```

## 7. Practical rule

For an external AI, the best CLI path is usually:
```bash
maurice workspace auth issue --organization <org_id>
maurice workspace list
maurice workspace bind <workspace_session_id>
maurice workspace call workspace_bootstrap_contract --arg goal=...
maurice workspace call workspace_feature_prepare --arg goal=... --arg intent_markdown='...'
maurice workspace call workspace_feature_apply --arg approved_plan_hash=<hash>
```
