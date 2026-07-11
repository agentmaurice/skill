# End-user authentication

Load this reference when a Workflow, MiniApp, or client application serves end
users through Firebase, Supabase, or another OIDC provider.

## Model auth at the Agent boundary

Declare which Agent surface accepts end-user identity, which provider verifies
it, and how claims map to organization, tenant, roles, and user identity.
Different Agents or capabilities may use different providers and policies.

Keep provider credentials outside the Agent Spec. Author only credential
references plus non-secret issuer, audience, algorithm, claim mapping, and
security requirements.

For Firebase, verify issuer and audience against the project. For Supabase,
verify the project issuer and intended audience. For generic OIDC, verify
issuer, JWKS, audience, algorithms, and claims explicitly.

## Verify the actual access surface

Before promising an authentication flow:

1. Read the compact capability contract for the target Agent.
2. Confirm that the Workflow, MiniApp, or viewer surface accepts the intended
   bearer identity.
3. Confirm tenant and role mapping.
4. Test rejection of an invalid issuer, audience, and tenant.
5. Verify that no runtime key or bearer is exposed to browser logs or Git.

If the desired UX and advertised runtime contract differ, report the mismatch
and stop before apply.
