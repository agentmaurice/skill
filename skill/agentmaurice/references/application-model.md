# AgentMaurice Application Model

Use this reference when the user talks about an "application" rather than a single recipe.

## 1. Core model

Do not equate these objects:
- application
- deployment
- meta-recette
- recipe

Use this hierarchy instead:
- application: the product the user wants to ship
- deployments: runtime targets for that product
- meta-recettes: blueprint slices of the product
- recipes: runtime definitions inside those blueprints
- client app repo: the public frontend project that consumes the exposed AgentMaurice surfaces

## 2. Practical rule

A real application may contain:
- one deployment with multiple meta-recettes
- multiple deployments with one meta-recette each
- multiple deployments and multiple meta-recettes

Examples:
- public app deployment plus admin deployment
- backoffice mini-app plus ingestion workflow backend
- review console plus scheduled summarizer

## 3. Meta-recettes as blueprints

Treat each meta-recette as a blueprint for one coherent capability slice.

Good slices:
- operator console
- intake workflow
- review workflow
- reporting dashboard
- scheduled summarization backend

Avoid assuming one giant meta-recette is always the right answer.

## 4. Application description directory

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
4. extract blueprint slices
5. map each slice to `mode=app` or `mode=recipe`
6. prepare changes slice by slice instead of flattening everything into one artifact
