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

## Missing secret

When a Workflow needs a secret that is not stored yet, open the masked page
and wait. Drop a `secret://` prefix. Run `maurice action request --kind
secret_input --resource <secret_ref> --constraint secret_ref=<secret_ref>
--json`, then `maurice viewer browser --human-action <action_id> --no-open`
in the background. Navigate to the exact printed loopback URL (full load of
host, port, and hash — not a hash-only edit on a previous secret page).
Confirm Ressource shows this `<secret_ref>` before handoff. Leave the
request's HTML `page_url` unused. Run `maurice action wait
--id <action_id> --follow` until `stored` or `cancelled`. One request per
secret, each with its own printed URL. The value stays in the browser and
the local keyring. It never enters the transcript, logs, Git, or MiniApp
state.
- Redact runner output before retention. A benchmark event must never contain a
  credential value.

## Using a stored secret

`stored` means the human saved the value. The `secret://` reference is still not the value. Do not read the vault, the keyring, `action show`, or the browser to recover it.

Consume it only through a tool that attaches it:

- A catalog connector exposes tools that send the saved key. After `stored`, call those tools with `maurice tools call` or, inside a Workflow, `callTool` and the exact name from `maurice tools list`. Do not pass the reference as an argument.
- Do not put `secret://…` in Deno `code_execution` context, code, or a `fetch` header. The sandbox keeps the reference unresolved. There is no `getSecret`, and a direct `fetch` cannot receive the raw credential.
- Do not arm a schedule until one real tool call that needs the credential has succeeded.
- Do not author `{"$binding":…}` until `maurice spec schema workflow` shows that expression. It is not in the current contract.

If no listed tool attaches this credential, stop and say the Workflow cannot call that API with the stored secret. Do not paste the key into the Workflow, the prompt, or the chat.

## Approval identity

An approval must identify a human principal and the exact immutable plan hash.
An agent or service principal cannot approve its own plan. In production, the
preparer and approver must be distinct principals.

If the platform cannot prove the approver identity, stop before apply.
