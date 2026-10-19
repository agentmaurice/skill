---
name: maurice-diagnostic
description: >-
  Run a quick, read-only fit diagnostic of the current codebase for
  AgentMaurice (Maurice): find where Compiled AI workflows, channels,
  MiniApps, AgentMaurice MCP servers, Company in a Box Modules or connected
  services would help, recommend one small first pilot, and say plainly where
  Maurice brings nothing. Needs no `maurice` binary. Use when someone asks
  whether AgentMaurice or Maurice fits their project, what they could do with
  it, or for /maurice-diagnostic.
---

# Maurice diagnostic

Maurice is AgentMaurice's runtime. Your assistant designs, Maurice compiles:
the AI reasons once while a workflow is built, then the workflow runs as code
for almost nothing, the same way every time, with AI judgement kept only where
judgement is needed.

This Skill gives a first opinion from the code alone. It does not install
anything and it does not replace `maurice doctor`, which describes an
installed instance. After installation, the authoring Skill `agentmaurice`
takes over from the report's JSON block.

## Hard rules

- Read only. Never edit, create, move or delete a file in the repository,
  except `maurice-diagnostic.md` at the root when the user explicitly agrees.
- Never open `.env`, `.env.*` (except `.env.example` / `.env.sample`), key
  files, credential stores, `secrets/`, or anything that looks like a secret.
  Read variable names only, never values.
- Run no command that writes, installs, builds, starts a service or calls a
  paid API. Read-only `git` and file listing commands are fine.
- Network: only the public AgentMaurice URLs listed in
  [references/sources.md](references/sources.md), plus this Skill's own files.
  If you read this file from a URL, resolve every `references/...` link
  against https://agentmaurice.ai/skill/maurice-diagnostic/. Nothing from the
  repository leaves the machine.
- Every opportunity cites at least one `path:line` you actually read. No
  evidence, no opportunity: put it under Questions instead.
- Recommend only capabilities marked available in the sources. Never promise
  automatic execution for a connected service that is not a governed pack.
- Never invent a customer-specific gain. You may cite the published reference
  measurement with its caveat (see the grid).

## Procedure

1. **Frame (1 minute).** Ask nothing unless the user gave no repository. Note
   the user's language and answer in it.
2. **Load sources.** Fetch the live sources from
   [references/sources.md](references/sources.md). If the network is
   unavailable, use the snapshots in `references/generated/` and say so with
   their date.
3. **Inventory (bounded).** Read manifests and lockfiles (`package.json`,
   `pyproject.toml`, `requirements*.txt`, `go.mod`, `Gemfile`, `pom.xml`,
   `composer.json`, `Cargo.toml`), entry points, `Dockerfile`/compose files,
   CI files, cron and scheduler definitions, `.env.example`, MCP configs, and
   assistant files (`CLAUDE.md`, `AGENTS.md`, `.cursor/`). Then search the
   source for the signals of the grid. Skip `node_modules`, `vendor`, `dist`,
   `build`, `.venv`, generated and minified files. Stop at about 300 files
   read; report what you skipped.
4. **Map.** Match findings to
   [references/capability-grid.md](references/capability-grid.md): signal,
   capability, concrete brick (MCP server, Module, connected service),
   prerequisite (Maurice on the computer, or a Console account).
5. **Score.** For each opportunity, score 1–3: volume, rules (deterministic
   share), current cost (a model called at each run), effort (inverted), risk
   (inverted). Mark evidence as `proven` (`path:line`), `likely` (dependency
   or name only) or `hypothesis` (goes to Questions).
6. **Choose one pilot.** Start small: high volume, high rules, low effort, low
   risk. One pilot only, with a measurable success criterion.
7. **Say where Maurice does not fit.** Use the anti-signals of the grid.
8. **Report.** Follow [references/report-format.md](references/report-format.md)
   exactly, in chat. Then offer to save it as `maurice-diagnostic.md`; write
   it only on a clear yes.

## Vocabulary

Use the public names: Maurice, Compiled AI (FR « IA compilée »), Workflow,
MiniApp, Module, Application, channels, swarm (FR « essaim », never "network"
/ « réseau »), vault (FR « coffre »), human approvals. An Agent Spec is the
versioned desired state of one Agent; a Module is a versioned package of
Workflows and MiniApps; a Skill is instructions for a coding agent, never a
runtime action.

## Next steps to offer

1. Install Maurice from this assistant: https://agentmaurice.ai/en/install/
   (FR: https://agentmaurice.ai/fr/installer/).
2. Run `maurice doctor --json`.
3. Hand the report's JSON block to the `agentmaurice` Skill to build the pilot.
4. Book a demo: https://calendly.com/mikaelmorvan-agentmaurice/30min
