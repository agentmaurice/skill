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

- `--context <name>` désigne explicitement un contexte MauriceCLI pour un
  appel. Le raccourci conversationnel `/maurice:maurice use <name>` doit être
  traduit en `--context <name>` sur l'appel suivant ; `maurice use` n'accepte
  pas de nom positionnel. N'exécute pas `maurice context use <name>` sans
  demande explicite : cette commande modifie le contexte par défaut.
- Une commande locale qui nécessite un chemin reçoit `--data-dir <path>`.
- `maurice start` et `maurice stop` doivent recevoir le `--data-dir` cible
  lorsque le chemin n'est pas déjà explicite dans la demande.
- Ne bascule jamais vers le contexte courant global comme fallback silencieux.
- Ne lis jamais un fichier de jeton et ne demande jamais une valeur secrète
  dans le chat.

Un changement de contexte CLI ne rebranche pas le MCP déjà connecté. Invalide les références et plans observés sur l’ancienne cible. Avant une exécution sur une autre instance, vérifie son endpoint et son mandat explicites, puis refais le préflight, `search` et `explain` sur cette connexion. Si elle manque, guide le branchement public `maurice assistant connect generic --config-file <private-mcp-config> --endpoint <endpoint> --token-file <private-token-file>` ; aucun droit nouveau n’est créé et aucun fichier global n’est remplacé implicitement.

## Accueil et usage

« Accueil » est informatif : il n'exécute aucune opération métier. Si utile,
affiche seulement l'état local avec `maurice status --json` ou
`maurice doctor --json`, sans transformer un exit code nul en preuve de
connexion, de grant, de job ou de résultat métier.

Pour sélectionner explicitement un contexte dans une commande, ajoute
`--context <name>` à cette commande. Ne modifie pas le contexte par défaut
pour réparer implicitement une cible absente.

Pour le parcours d'une capacité AgentMaurice déjà branchée, suis strictement :

1. `maurice.search` — références visibles par le mandat ;
2. `maurice.explain` — cible, schémas, politique, `plan_hash`, effets ;
3. `maurice.execute` — seulement la référence expliquée, avec entrée validée,
   `idempotency_key` et, si fourni, `expected_plan_hash`.

Lis toujours `structured_content` lorsqu'il existe. `pending` reste une
attente humaine : utilise `maurice.explain` sur `pending_action:<id>` pour
observer son état et présente le lien de décision renvoyé par l'origine
explicitement fournie par le One, sous la forme `/one/#/human-action/<id>`.
Ne déduis jamais cette origine, son port ou ce lien depuis le port MCP.
Si `decision` vaut `rejected`, arrête le parcours ; ne réessaie pas avec une
autre référence ou une nouvelle clé. Une carte `completed` n'est pas une
approbation et une approbation n'est pas le résultat de l'exécution.

Le produit s'appelle AgentMaurice One ; les outils MCP peuvent avoir un nom
préfixé `one_`. Ne remplace jamais ce vocabulaire par un outil inventé comme
`one_legacy`.

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
  `maurice app workflow run <applicationKey> <workflowId> [--input-file <path>]`
  lorsque l'utilisateur a fourni ces références exactes. `--input` accepte
  aussi un objet JSON ; `--app-key` ou `--operator` suivent le contrat de la
  commande.
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
- Pour `new`, demande d’abord le type et la cible : Agent, Application ou Module.
  Une Application suit le [rail App](../agentmaurice/references/app-delivery.md) ;
  `maurice app init <applicationKey>` est une création distante, à autoriser
  explicitement. Un Module suit le [rail Module](../agentmaurice/references/modules.md) ;
  `maurice module init <moduleKey> --dir <path>` prépare un dépôt local.
  Ne confonds jamais scaffold local, création distante et déploiement.
- **check** : `maurice spec check --env <env> --agent-alias <alias> --dir <path> --json`.
- **plan** : `maurice spec plan --env <env> --agent-alias <alias> --dir <path> --json`.
- **apply** : `maurice spec apply --plan <plan-id> --dir <path> --json`,
  uniquement après l'approbation humaine du plan persistant. Les options
  `--approval-id`, `--target`, `--tests` et `--idempotency-key` restent celles
  affichées par `maurice spec apply --help`.
- **verify** : `maurice spec verify --plan <plan-id> --dir <path> --wait --json`.
- **test** : utilise `maurice test` et sa sous-commande affichée par
  `maurice test --help`; ne remplace pas le test déclaré par le plan.

Avant `check`, lis la spec, le lock, l'environnement, l'Agent cible, les
Workflows/MiniApps et le test plan. Un plan invalide, expiré, en conflit ou
`awaiting_approval` arrête le parcours. Le client n'approuve jamais à la
place de la personne.

Références canoniques du paquet : [front door](../agentmaurice/references/frontdoor.md)
et [Agent Spec V2](../agentmaurice/references/agent-spec-v2.md).

## Rapport

Pour chaque parcours, rapporte la commande ou l'outil réellement utilisé, la
cible explicite, le code de sortie, le statut structuré et la preuve obtenue.
Sépare toujours raccordement, plan, approbation, apply, verify, exécution et
qualification. Si l'interface demandée n'existe pas, indique l'invocateur
public le plus proche et le manque exact, sans fabriquer une équivalence.
