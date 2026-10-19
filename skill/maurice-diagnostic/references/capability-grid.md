# Signal → capability grid

Search the repository for these signals. Each match needs a `path:line` you
read. "Brick" names the concrete AgentMaurice piece; "Needs" is the
prerequisite: **Maurice** (free, on the computer, or on a hosted plan) or a
**Console account** (connected services).

| # | Signal in the code | How to spot it | Capability | Brick | Needs |
|---|---|---|---|---|---|
| 1 | A model called again and again on a rule-based task (classify, extract, check, validate, route) | `openai`, `anthropic`, `mistralai`, `google-genai`, `langchain`, `litellm` inside a loop, batch, queue worker or cron; prompt + JSON parsing; `temperature=0`; retries on parse errors | **Compiled AI**: a Workflow built once, then run as code | MCP `decision` for the short judgement that must stay AI | Maurice |
| 2 | Business scripts, cron jobs, batches | `crontab`, `schedule:` in CI, Airflow DAGs, Celery beat, `node-cron`, APScheduler, n8n or Zapier exports, `scripts/*.py` | **Workflow**, scheduled | — | Maurice |
| 3 | Home-made agents | tool-calling loops, LangGraph, CrewAI, AutoGen, OpenAI Agents SDK; cost or latency logs, timeouts | **Agent mode** for open tasks + compiled Workflows for the deterministic parts | — | Maurice |
| 4 | Messaging bots | `slack_bolt`, `@slack/bolt`, `telegraf`, `python-telegram-bot`, `discord.js`, WhatsApp Business API, Google Chat, Signal | **Channels** | — | Maurice |
| 5 | Inbound HTTP, webhooks, IoT | `/webhook` routes, internal HTTP handlers, MQTT clients (`paho-mqtt`, `mqtt.js`) | **Channels**: HTTPS API, MQTT | MCP `api` when an OpenAPI contract exists | Maurice |
| 6 | Small internal interfaces | Streamlit, Gradio, Retool exports, admin pages, data-entry forms | **MiniApps** | — | Maurice |
| 7 | Human validation coded by hand | statuses like `pending_approval`, "please validate" emails, manual flags, approval tables | **Human approvals** (allowed, refused, revoked, approved) | — | Maurice |
| 8 | Model keys scattered across services | several provider key names in `.env.example` or CI variables (names only) | **Vault**, bring your own keys | — | Maurice |
| 9 | MCP already in use | MCP servers or clients, `mcp.json`, `.mcp.json` | **Connect everywhere**: Maurice uses and exposes MCP | MCP catalog | Maurice |
| 10 | Work delegated between teams, sites or entities | cross-entity service calls, inter-team task queues | **Swarm** (Maurice to Maurice, approved links, signed answers) | — | Maurice |
| 11 | Directory, roles, rights, approvals, shared case files rebuilt by hand around internal tools | `roles`, `permissions`, `audit_log`, `case`/`dossier` tables in non-core internal tools | **Organisation bricks** (identities, roles, rights, approvals, shared files, memory, audit) | Modules `cib-enterprise-admin`, `cib-work-dossiers`, `company-memory` | Maurice |
| 12 | Repetitive watch, content, customer follow-up, launch marketing, daily routine | scripts that import sources, draft content, follow accounts, log time | **Workflows + MiniApps** | Modules `cib-veille`, `cib-contenu`, `cib-accompagnement`, their memory connections `cib-veille-memory`, `cib-contenu-memory`, `cib-accompagnement-memory`, plus `cib-daily-routine`, `cib-marketing-launch` | Maurice |
| 13 | SaaS SDKs or APIs already used | `googleapis`, `@hubspot/api-client`, `airtable`, `@notionhq/client`, `jsforce`, `stripe`… | **Connected services** | Integrations catalog: governed pack, directory, or absent → MCP `api` with an OpenAPI contract | Console account |
| 14 | Tooling needs | OCR (`tesseract`, `pdfplumber` on scans), office conversion (`python-docx`, `openpyxl`), home-made RAG or embeddings, scraping (Playwright, Selenium), SSH scripts (`paramiko`, `fabric`), CSV/JSON profiling (`pandas`), PII regexes, report generation, OTLP traces, shared SQL memory | **Workflow with tools** | MCP `ocr`, `document`, `rag`, `search`, `brain`, `browser`, `ssh`, `data`, `guard`, `artifact`, `observe`, `memory` (check `one_compatible` in the catalog) | Maurice |
| 15 | A coding assistant already in place | `CLAUDE.md`, `AGENTS.md`, `.cursor/`, `.codex/` | Entry point: Maurice installs from the assistant | — | — |

## Reading the bricks

- **MCP servers**: use `catalog.json`. Cite the server `slug`, its version and
  one relevant tool. If `one_compatible` is false, say "not yet available on
  Maurice on the computer" and do not make it the pilot.
- **Company in a Box Modules**: reusable Modules of Workflows and MiniApps for
  the organisation of a company, never business-specific packs. Installation
  is guided (composition into the consuming project, then the Agent Spec
  rail); installation by URL is not offered. HR, Sales and sector packs are not
  delivered: never suggest them.
- **Connected services**: available to Console accounts only. A governed pack
  runs its actions under an explicit policy; a directory provider can be
  connected but each action asks for authorisation. Without the integrations
  catalog, write "connectable through the Console, to be checked" and promise
  nothing more.

## Anti-signals

Say them plainly in "Where Maurice brings nothing":

- The model *is* the product, on creative, never-repeated work.
- Sub-second latency is critical in the core loop.
- The real need is to replace an ERP, invoicing or accounting tool: Maurice
  connects to them, it does not replace them.
- The team only uses Windows computers (Maurice on Windows is coming soon) or
  Intel Macs (not yet).
- The volume is too low for compilation to pay off (a task run a few times a
  month).

## Scoring

| Criterion | 1 | 2 | 3 |
|---|---|---|---|
| Volume | a few runs a month | daily | hundreds or more a day |
| Rules | mostly judgement | mixed | mostly exact rules |
| Current cost | no model call | a model call sometimes | a model call at every run |
| Effort (inverted) | 4+ systems to connect | 2–3 systems | 1 system or files only |
| Risk (inverted) | irreversible side effects, sensitive data | reversible writes | read-only or draft output |

Pilot = the best total among opportunities with Rules ≥ 2 and Effort ≥ 2.

## Reference measurement

You may cite it, never extrapolate it to the user's case: checking 1,000
orders cost €16.22 with a Sonnet 5.5 agent, €1.27 with Haiku 5.5, and €0.07
once compiled by Maurice (about 1.1 s instead of about 7 s). One scenario only.
Source: https://agentmaurice.ai/en/articles/ai-agents-think-once/ (FR:
https://agentmaurice.ai/fr/articles/agents-ia-reflechir-une-fois/).

Never mention a capability that is absent from this grid or from the live
sources, and never promise a hosted-plan service level (backups, support,
per-plan features) in a diagnostic.
