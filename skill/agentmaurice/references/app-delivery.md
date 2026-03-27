# AgentMaurice App Delivery

After the app is prepared, verified, and deployed, the final answer should read like a delivered product handoff.

## The answer should include

- what was built
- the application map
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

## Keep the close-out practical

Prefer this shape:
- Built
- Application map
- Access
- Verified
- Gaps or assumptions
- Next steps

Do not stop at "plan applied" when the user asked for an application outcome.
