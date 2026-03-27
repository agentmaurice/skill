# AgentMaurice App Intake

Use this reference when the user provides an app idea but not enough implementation detail.

## Ask only blocking questions

Capture or infer:
- what the application boundary is
- whether there are multiple deployments
- whether there are multiple blueprint slices
- whether end users authenticate directly to AgentMaurice-backed surfaces
- who uses the app
- what they input or review
- what the app produces
- what actions the app must support
- what external systems or MCP tools are required

Good blocking questions:
- Does this app need one deployment or separate deployments for public, admin, or backend roles?
- Should this be one blueprint slice or several meta-recettes with separate responsibilities?
- Do end users sign in with Firebase, Supabase, or another OIDC provider?
- Who is the primary user of this app?
- What is the single most important action they need to perform?
- What data source or external tool must be connected on day one?

Avoid asking unless necessary:
- full UI copy
- complete field-by-field schemas
- comprehensive roadmap questions
- detailed styling preferences

## Sensible defaults

If the user stays high-level:
- assume a single main workflow
- assume one main screen plus detail or result view
- assume OpenUI for interactive mini-app delivery
- assume verification should happen before apply

If the user provides an application description directory:
- read it before asking more questions
- prefer extracting structure from the directory over asking for information that is already written down

## Intent-to-runtime shortcut

Examples:
- "I want a dashboard for support leads" -> mini-app
- "I need a tool to review invoices and approve or reject them" -> mini-app
- "I want an assistant that summarizes tickets every hour" -> workflow backend
- "I need a backend that classifies inbound requests" -> workflow backend
