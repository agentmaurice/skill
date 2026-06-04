# AgentMaurice Application Model

Use this reference when the user talks about an "application" rather than a single recipe.

## 1. Core model

Do not equate these objects:
- application
- Application
- module
- Module Catalog entry
- deployment
- Agent Spec / meta-recette
- recipe

Use this hierarchy instead:
- application: the product the user wants to ship
- Application: an AgentMaurice runtime resource composed of modules
- module: an installable unit described by `agentmaurice.module/v1`
- Module Catalog entry: an organization-scoped record of module manifest,
  source URL, requested ref, resolved commit SHA, content hash, visibility,
  version, and provenance
- deployments: runtime targets for that product
- Agent Spec / meta-recette: the canonical blueprint for one deployment in V1
- recipes: runtime definitions inside that blueprint
- client app repo: the public frontend project that consumes the exposed AgentMaurice surfaces

## 2. Practical rule

A real application may contain:
- one deployment with one canonical Agent Spec
- multiple deployments with one canonical Agent Spec each
- several conceptual slices represented inside the relevant deployment specs
- one AgentMaurice `Application` composed of modules, where each installed
  module maps to one deployment

Examples:
- public app deployment plus admin deployment
- backoffice mini-app plus ingestion workflow backend
- review console plus scheduled summarizer
- booking module plus user module inside the same runtime `Application`

## 3. Agent Specs as blueprints

Treat each deployment Agent Spec / meta-recette as the complete declarative
blueprint for that deployment. It may contain several conceptual slices, but
the `structured_spec.recipes_definitions` set must remain complete.

Good slices:
- operator console
- intake workflow
- review workflow
- reporting dashboard
- scheduled summarization backend

Avoid splitting a single deployment into several competing meta-recettes in V1.
Use separate deployments when isolation or ownership requires separate runtime
targets.

## 4. Modular Applications

Use the modular Application model when the user wants:
- reusable business modules
- a module catalog
- several independently developed modules assembled into one product
- public or private Git module sources
- repeated deployment of the same functional module for different customers

Core invariants:
- schema versions are `agentmaurice.module/v1`,
  `agentmaurice.application/v1`, and `agentmaurice.module-catalog/v1`
- Module Catalog is separate from Skill Catalog
- each installed module maps to a deployment with one canonical Agent Spec
- runtime routes are generic and manifest-driven
- end-user auth remains deployment-scoped in V1
- private Git access uses credential refs, never raw secrets in files

The runtime lookup is:
`application_key -> module_key -> capability_key -> deployment -> recipe or mini-app`.

Do not invent module-specific backend routes. A module declares capabilities;
AgentMaurice exposes generic action, query, and app runtime endpoints.

## 5. Application description directory

If the user has a directory in the repo that textually describes the application, treat it as the build source of truth.
Look first for a canonical file named `agentmaurice.app.md`.

Typical useful contents:
- product overview
- user roles
- deployment map
- blueprint list
- data sources
- external integrations
- acceptance criteria

The AI should:
1. read `agentmaurice.app.md` first
2. if needed, read the rest of the directory
3. extract deployment topology
4. extract conceptual blueprint slices
5. map each slice to `mode=app` or `mode=recipe`
6. prepare changes slice by slice while preserving the complete Agent Spec for
   each target deployment
