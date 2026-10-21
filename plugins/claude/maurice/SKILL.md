---
name: maurice
description: >-
  Piloter AgentMaurice depuis Claude Code avec une cible explicite : accueil,
  diagnostic, découverte MCP, exécution gouvernée, swarm AgentJob et cycle
  Agent Spec.
---

# Maurice

Ce skill est invoqué comme `/maurice:maurice`. Il guide le client Claude Code
vers les interfaces publiques déjà livrées. Il ne crée aucun serveur MCP, ne
contourne aucune autorisation et ne remplace pas l'approbation humaine.

## Règles de cible

Toute action qui parle à un One, un deployment, une Application ou un Agent
doit nommer sa cible. Conserve la référence complète renvoyée par la
découverte ; ne déduis jamais une cible depuis son nom affiché.

- `--context <name>` désigne explicitement un contexte MauriceCLI.
- Une commande locale qui nécessite un chemin reçoit `--data-dir <path>`.
- `maurice start` et `maurice stop` doivent recevoir le `--data-dir` cible
  lorsque le chemin n'est pas déjà explicite dans la demande.
- Ne bascule jamais vers le contexte courant global comme fallback silencieux.
- Ne lis jamais un fichier de jeton et ne demande jamais une valeur secrète
  dans le chat.

## Accueil et usage

« Accueil » est informatif : il n'exécute aucune opération métier. Si utile,
affiche seulement l'état local avec `maurice status --json` ou
`maurice doctor --json`, sans transformer un exit code nul en preuve de
connexion, de grant, de job ou de résultat métier.

Pour sélectionner explicitement un contexte, utilise `maurice use <name>`.
Ne l'utilise pas pour réparer implicitement une cible absente.

Pour le parcours d'une capacité AgentMaurice déjà branchée, suis strictement :

1. `maurice.search` — références visibles par le mandat ;
2. `maurice.explain` — cible, schémas, politique, `plan_hash`, effets ;
3. `maurice.execute` — seulement la référence expliquée, avec entrée validée,
   `idempotency_key` et, si fourni, `expected_plan_hash`.

Lis toujours `structured_content` lorsqu'il existe. `pending` reste une
attente humaine. Une carte `completed` n'est pas une approbation et une
approbation n'est pas le résultat de l'exécution.

## Doctor

Pour diagnostiquer la porte MCP locale, les deux options sont obligatoires et
explicites :

```bash
maurice doctor --mcp-endpoint <endpoint> --mcp-token-file <private-token-file> --json
```

Le fichier de jeton reste privé ; le client ne le lit ni ne l'imprime. Lis
`mcp_frontdoor.checked` et `mcp_frontdoor.ok`. Doctor prouve le handshake et
le catalogue accessibles, jamais une exécution Workflow, un grant effectif,
une qualification métier ou la disponibilité d'une VM.

## Swarm et jobs

Il n'existe pas de façade publique `maurice swarm` ni de commandes
`node jobs/logs/run`. Ne les invente pas et n'appelle pas directement une
route HTTP ou la base.

- `swarm status` : combine uniquement des lectures ciblées, selon la demande :
  `maurice status --json`, `maurice doctor --json`, ou l'état d'un graphe.
- `swarm nodes` : `maurice access list --me --json` expose la projection des
  nœuds de l'accès personnel ; `maurice node show [--data-dir|--edge] --json`
  expose l'identité locale. Cela ne constitue pas un inventaire générique du
  swarm.
- `swarm run` : utilise `maurice.execute` après `search` puis `explain`, ou
  une commande publique `maurice app run <applicationKey> <workflowId>` lorsque
  l'utilisateur a fourni ces références exactes.
- `swarm jobs` et `swarm logs` : exige `job_id` ou `graph_id`, puis utilise
  `maurice job graph get <graph_id>` et `maurice job graph events <graph_id>`
  pour un graphe, ou les outils MCP `inception_tasks_get` et
  `inception_tasks_events`. Il n'y a pas de `job list` ou de `job logs` à
  fabriquer.
- La soumission et l'annulation restent bornées par les interfaces existantes
  (`maurice job graph submit`, `cancel`, `raise-budget` ou les outils MCP
  `inception_tasks_submit` et `inception_tasks_cancel`) et leurs contrats.

## Lifecycle local

`maurice start`, `maurice stop` et `maurice status` pilotent l'instance One
locale ; `maurice edge serve|connect|disconnect` pilotent le pont Edge. Edge
ne démarre pas One. Un chemin local explicite est requis avant `start` ou
`stop`. Ne lance jamais un serveur avec `go run`, `./bin/agentmaurice serve`
ou un kill manuel.

## Build Agent Spec

Il n'existe pas de commande publique `maurice build`. Le mot « build » est un
raccourci conversationnel vers les rails ci-dessous :

- **new** : pour créer un Agent, commence par l'observation et la planification
  d'architecture (`inception_architecture_*`), avec `create_agent` dans le
  plan ; une approbation humaine distincte est nécessaire. Pour un Agent
  existant seulement, `maurice spec init` crée l'état d'authoring local ; il
  ne crée pas un Agent distant.
- **check** : `maurice spec check --env <env> --agent-alias <alias> --dir <path> --json`.
- **plan** : `maurice spec plan --env <env> --agent-alias <alias> --dir <path> --json`.
- **apply** : `maurice spec apply --env <env> --agent-alias <alias> --dir <path> --json`,
  uniquement après l'approbation humaine du plan persistant.
- **verify** : `maurice spec verify --env <env> --agent-alias <alias> --dir <path> --json`.
- **test** : utilise `maurice test` et sa sous-commande affichée par
  `maurice test --help`; ne remplace pas le test déclaré par le plan.

Avant `check`, lis la spec, le lock, l'environnement, l'Agent cible, les
Workflows/MiniApps et le test plan. Un plan invalide, expiré, en conflit ou
`awaiting_approval` arrête le parcours. Le client n'approuve jamais à la
place de la personne.

## Rapport

Pour chaque parcours, rapporte la commande ou l'outil réellement utilisé, la
cible explicite, le code de sortie, le statut structuré et la preuve obtenue.
Sépare toujours raccordement, plan, approbation, apply, verify, exécution et
qualification. Si l'interface demandée n'existe pas, indique l'invocateur
public le plus proche et le manque exact, sans fabriquer une équivalence.
