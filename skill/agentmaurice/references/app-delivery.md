# AgentMaurice App Delivery

After the app is prepared, verified, and deployed, the final answer should read like a delivered product handoff.

## The answer should include

- what was built
- the application map
- if modular, the `Application` key and installed modules
- which runtime was chosen: `mode=app` or `mode=recipe`
- which deployment was targeted
- which blueprint slice or meta-recette was changed
- what end-user auth was assumed or configured
- what was verified
- how to access it
- the most important next steps

## For mini-apps

Return:
- the mini-app framing
- the deployment it belongs to
- the blueprint slice it represents
- whether end-user bearer auth is part of the intended access path
- viewer bootstrap or app access path when available
- whether OpenUI delivery is intended
- what was previewed or runtime-tested

## For workflow backends

Return:
- the backend framing
- the deployment it belongs to
- the blueprint slice it represents
- whether callers use bearer JWT, API key, or both
- the recipe or execution surface
- how to invoke it
- what runtime checks were performed

## For modular Applications

Return:
- the `Application` key and display name
- installed module keys and versions
- catalog entry IDs
- source URLs, requested refs, resolved commit SHAs and module hashes
- deployments created or updated for each module
- declared capabilities per module: actions, queries and apps
- end-user auth assumptions, especially deployment-scoped auth propagation
- whether `maurice app plan`, approval and `maurice app apply` were completed
- `maurice app status` and `maurice app docs` findings
- runtime capability verification performed through generic Application routes

## Keep the close-out practical

Prefer this shape:
- Built
- Application map
- Access
- Verified
- Gaps or assumptions
- Next steps

Do not stop at "plan applied" when the user asked for an application outcome.
