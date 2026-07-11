# Frontend starter

Load this reference when the application needs a client frontend. Prefer an
existing AgentMaurice viewer package over inventing an unrelated client stack.

Use the package matching the delivery boundary:

- `viewer-demo` for a runnable standalone starter;
- `viewer-web` for integration into an existing React application;
- `viewer-embed` for a web component embedded into an existing site;
- `viewer-core` for an advanced custom integration.

Ground the integration in the runtime contract returned for the Agent or
Module. Use public Agent, Application, Module, Workflow, and MiniApp keys. Do
not copy internal storage identifiers into client code.

Keep runtime access keys separate from end-user bearer identity. Never commit
either value. Use the advertised auth adapter and secret injection mechanism.

Before handoff, verify bootstrap, authentication, initial state, event
dispatch, error rendering, reduced motion, and a production build. Document
which repository owns branding and client-specific auth integration.
