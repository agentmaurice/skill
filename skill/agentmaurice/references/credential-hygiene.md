# Credential Hygiene

Use this reference when issuing or handling AgentMaurice credentials.

## Workspace Control credentials

- `maurice workspace auth issue` defaults to `--role readonly`.
- Request `--role operator` or `--role admin` only when the task explicitly
  needs it.
- Prefer `--deployment <deployment_id>` for production work. A scoped
  credential cannot bind, target, or call tools for another deployment.
- Do not ask the user to paste raw Workspace Control tokens back into chat.
- Store local CLI credentials only through MauriceCLI config; the config
  directory must be private and the config file must be user-readable only.

## Approval identity

- Workspace Control approval principals are `cred:<credential_id>` when a
  credential is available.
- `user:<user_id>` is only a fallback.
- In production, the approver must be a different principal from the preparer.
- `workspace_session_approve_prepared_plan` requires the exact `plan_hash`.

## Secret handling

- Never write raw API keys, bearer tokens, Git credentials, provider secrets,
  SSH private keys, or database passwords into prompts, logs, manifests, lock
  files, test fixtures, or final answers.
- Store credential references only: IDs, aliases, scopes, expiry and status are
  acceptable; secret values are not.
