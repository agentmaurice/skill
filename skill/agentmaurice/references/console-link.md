# Console link without a browser

Load this reference when a local One must be linked to the Console and no
browser can open on the machine that runs it: a headless server, a container,
an SSH session with no display, or a remote development VM. Also load it when
`maurice doctor` reports `console_binding.not_linked` and proposes the next
action `console_link`.

## Decide first

```bash
maurice console status --json
```

- error `console_link_no_target` — no local One was found; start one with
  `maurice start` (or pass `--api <url>`), then check again.
- `linked: true` — stop. Do not link again. Re-pair with `--force` only when the
  person explicitly asks to replace the existing binding.
- `pairing_supported: false` — this One has no data directory or encryption key
  and cannot pair (exit 10). Report it; do not work around it.
- `linked: false` with `pairing_supported: true` — run the link command below.

When the person works at a machine with a local browser, the One home page
(`maurice home`, loopback only) already has a pairing screen. Use
`maurice console link` for the no-browser case, not instead of that page.

## Link

```bash
maurice console link --json
```

The command asks the local One to start a device-code pairing, then waits for
the approval. On stderr it prints `Open <verification URL> and enter code:
<user code>`, a note when no local browser is detected, and the waiting time.
With `--json`, stdout carries a single final document (`status: paired` and the
binding), so read the URL and the code from stderr.

1. Give the person the verification URL and the user code exactly as printed.
2. The person opens the URL on their own machine, signs in there, enters the
   code, and approves.
3. Keep the command running for the printed waiting time (run it in the
   background when your runtime limits a foreground call, and read its output).
   It ends when the person approves, refuses, or the code expires.
4. Confirm with `maurice console status --json`: `linked` must be `true`.

Optional flags: `--device-name` (the name shown on the Console, default the host
name), `--console-url` (only a Console the person named, or the One's own
configured Console), `--force` (see above).

| Exit | Meaning | Next step |
|---|---|---|
| 0 | paired | verify with `maurice console status` |
| 7 | already linked | stop unless the person asked to re-pair (`--force`) |
| 8 | refused on the Console | stop and ask; do not retry in a loop |
| 9 | code expired | run the command again for a fresh code |
| 10 | this One cannot pair | report; needs a data directory and an encryption key |
| 11 | Console unreachable | check the network or `--console-url`, then retry once |
| 12 | interrupted | run it again |

## Rules

- Never ask for, receive, type, or store the person's Console credentials:
  e-mail, password, sign-in codes, or session cookies. They sign in on their own
  machine.
- Never drive a browser for the person (no browser automation, no computer use)
  to open the verification URL or to approve it.
- The user code is meant to be shown to the person. The device code is never
  printed; do not try to read it from the One, its logs, or its API.
- Do not commit the verification URL or the code, and do not paste them into
  tickets or logs: they are short-lived approval material.
- Linking does not buy anything. Credits, plans, and payment stay with the
  person on the Console; do not choose or purchase them.
