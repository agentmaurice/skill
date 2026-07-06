# AgentMaurice Operating Contract

> Generated from internal/operatingcontract. Do not edit manually.

- Schema: agentmaurice.operating_contract/v1
- Version: 2026-06-10.1
- Hash: 2ea506e2899777ef2fd1be0447a070bf4ba989e34acea8811ca3ef7c96327986

# Shared AgentMaurice Operating Contract

Use this contract whenever an AI operates AgentMaurice through Calisto, External Inception, Workspace Control, or MauriceCLI.

Core rules:
- Start every deployment task with runtime grounding: deployment scopes, Doctor with `format=ai_contract`, and MCP capabilities.
- Never infer an organization, environment, deployment, or deployment alias from a human label when an explicit ID, alias, or scope contract exists.
- Treat the Agent Spec / `meta_recette` structured spec as the governed source of truth for recipes managed by AgentMaurice.
- Use compile, plan, approval, apply, test, and reconcile workflows instead of ad hoc runtime mutation.
- Present concrete impact and scope before governed mutations unless the current user request already explicitly approves apply/reconcile/resync now.
- Preserve secrets: never print raw API keys, bearer tokens, Git credentials, provider secrets, SSH keys, or database passwords in prompts, logs, manifests, locks, or user-facing answers.
- If a tool reports a permission boundary, explain the boundary and do not invent a workaround.
- Prefer concise answers grounded in tool results. Keep raw discovery JSON internal unless the user explicitly asks for it.
- Use exact tool names returned by capabilities, Doctor, `inception_search`, or generated SDK metadata. Never abbreviate, translate, or invent tool names.

Operational defaults:
- For diagnostics, report scope, runtime status, important configuration, missing capabilities, and next action.
- For Agent Spec changes, discover available tools before writing recipes and list explicit assumptions in the spec.
- For sensitive actions, require explicit confirmation unless the user already requested the apply/delete/rotation/resync operation in the current turn.

# External Code Agent Operating Contract

Use this section for Codex, Claude Code, Cursor, Windsurf, generic MCP clients, or any external AI connected through MauriceCLI or agent-discovery.

Connection surfaces:
- If the user provides an `agent-discovery` bootstrap URL (`amb_...`), consume it once, read `agentmaurice.agent_discovery/v1`, follow `instructions_markdown`, and configure/use External Inception if possible.
- If the user provides `maurice agent connect ...` or `maurice env connect ...`, use MauriceCLI and the Git-native project it initializes.
- If an External Inception MCP server is already connected, use only the deployment scopes it exposes. The server can be named `agentmaurice-inception` or `agentmaurice-inception-<env>-<deployment-alias>`.
- If Workspace Control is connected, prefer it for organization/workspace-aware Calisto operations.
- If MCP is unavailable, fall back to MauriceCLI commands.

Git-native workflow:
- If `agentmaurice.yaml` exists, read it with `agentmaurice.lock.json`, `environments/<env>.yaml`, `deployments/<deployment-alias>/agent-spec.json`, and deployment recipe files before proposing changes.
- Use `maurice spec pull/validate/plan/approve/apply/status` for Agent Spec changes.
- Never write credentials into project manifests, lock files, logs, prompts, or responses.
- For governed changes, produce or read the `plan_hash`, get explicit approval, then apply with that exact hash.

MCP workflow:
- Start with `inception_deployment_scopes_list`, `inception_deployment_doctor(format=ai_contract)`, and `inception_mcp_capabilities`.
- Discover exact schemas with `inception_search` before `inception_call` when uncertain.
- In code-mode clients, route through `inception_search` and `inception_call` rather than raw individual Inception tools.
- Call runtime tools through `inception_runtime_tool_call`, not by sending their raw names as Inception operation names.

Build workflow:
- For an application idea, classify whether it is a mini-app/OpenUI, workflow backend, modular Application, or deployment Agent Spec.
- Prefer a delivered application or governed apply plan over a static draft, unless the user asks for draft-only.
- Validate/test after apply and compare runtime traces, logs, cost, and latency when available.
