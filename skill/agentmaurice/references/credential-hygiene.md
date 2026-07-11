# Credential hygiene

Load this reference whenever Agent Spec authoring, a Module, or a client
integration needs credentials.

## Rules

- Never write API keys, bearer tokens, Git credentials, provider secrets, SSH
  private keys, database passwords, or secret environment values into Git,
  prompts, logs, test fixtures, plans, events, or user-facing answers.
- Store only a credential reference: identifier, alias, scope, expiry, status,
  and provider metadata may be reviewed; the value may not.
- Keep MauriceCLI credentials in its private local configuration. Require
  user-only file permissions.
- Scope credentials to the organization, environment, Agent, and capability
  needed by the task. Do not broaden scope for convenience.
- Do not ask the user to paste a raw token into chat. Prefer a secret-file,
  environment, keychain, or interactive credential flow advertised by the CLI.
- Redact runner output before retention. A benchmark event must never contain a
  credential value.

## Approval identity

An approval must identify a human principal and the exact immutable plan hash.
An agent or service principal cannot approve its own plan. In production, the
preparer and approver must be distinct principals.

If the platform cannot prove the approver identity, stop before apply.
