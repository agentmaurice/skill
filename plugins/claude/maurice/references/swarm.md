# Référence opératoire : intentions swarm

Ce document décrit les interfaces CLI exposées dans le backend de qualification
AGENT-1034 pour les intentions conversationnelles `swarm status`, `swarm
nodes`, `swarm run`, `swarm jobs`, `swarm logs`, `start` et `stop`. La qualification dépend du binaire et du One utilisés ; consulter les preuves AGENT-1034. La release générale reste distincte. Ne fabrique pas
une route privée, un accès direct à la base ou un outil MCP absent du catalogue.

Le groupe natif CLI est `maurice swarm`. Le profil optionnel
`maurice client-mcp-stdio` ne constitue pas un nouveau backend : il projette
seulement les opérations locales explicitement autorisées par sa configuration.
Par défaut il expose les lectures ; `--allow-local-write` ajoute les scaffolds
et apply locaux, et `--allow-local-lifecycle` ajoute start/stop. Il ne fournit
pas `swarm run`, n'accepte pas de shell RPC et n'effectue aucune approbation.

Exemples de commandes natives à privilégier :

```text
maurice swarm status --json
maurice swarm nodes --json
maurice swarm run <ref> --input-file <input.json> --idempotency-key <key> --json
maurice swarm jobs list --json
maurice swarm jobs get <job-id> --json
maurice swarm jobs events <job-id> --json
maurice swarm logs <job-id> --json
maurice swarm start --data-dir <one-data-dir> --json
maurice swarm stop --data-dir <one-data-dir> --json
```

Les alias historiques `maurice status`, `maurice node show`, `maurice start`
et `maurice stop` restent utilisables lorsque leur cible explicite est adaptée.

Toutes les actions doivent nommer leur cible. Pour une commande locale,
fournis `--data-dir <path>` quand le chemin n'est pas déjà explicite. Pour un
appel distant, conserve la référence complète renvoyée par la découverte et
le contexte MCP qui l'a produite. Ne déduis jamais une cible depuis son nom
affiché et ne change jamais silencieusement de contexte.

## Choisir le catalogue MCP

Utilise le catalogue correspondant à la connexion déjà ouverte :

- Une connexion front door expose exactement `maurice.search`,
  `maurice.explain` et `maurice.execute`. Elle sert à découvrir une capacité,
  lire son plan et l'exécuter après contrôle du mandat.
- Une connexion External Inception ouverte par une clé d'Application en
  `X-API-Key` peut être une session runtime D1. Son catalogue expose exactement
  `inception_tasks_capabilities`, `inception_tasks_submit`,
  `inception_tasks_get`, `inception_tasks_events` et
  `inception_tasks_cancel`. Une session builder ne les expose pas.

Ne mélange pas les deux catalogues. Une clé d'Application ne crée pas un
nouveau droit, une autre Application ou un principal arbitraire. Le serveur
revalide l'Application, la clé, les scopes et l'organisation à chaque appel ;
une révocation doit donc arrêter les nouveaux appels.

## `swarm status`

Choisis une lecture selon la cible demandée :

```text
maurice status --json --data-dir <one-data-dir>
maurice doctor --json --data-dir <one-data-dir>
maurice job graph get <graph-id> --json
```

`status` renvoie le statut de l'instance One locale (`running`, `pid`,
`data_dir`). `doctor` ajoute le diagnostic local et, quand ses paramètres sont
résolus, des vérifications de readiness ou de contexte ; il ne prouve pas une
exécution de Workflow. `job graph get` ou `inception_tasks_get` donne l'état
d'un graphe identifié, ses phases, ses nœuds, sa révision et les résultats
disponibles.

Ces lectures ne constituent pas un inventaire générique d'un swarm. Si aucun
`graph_id` ou `job_id` n'est connu, explique la limite au demandeur au lieu de
fabriquer une liste.

## `swarm nodes`

La projection personnelle et l'identité locale sont les deux surfaces
publiques prévues :

```text
maurice access list --me --json
maurice node show --json --data-dir <one-data-dir>
maurice node show --json --edge
```

`access list --me` renvoie les Applications, verdicts, tokens d'assistant et
nœuds visibles par la personne connectée. `--limit` et `--offset` bornent la
page ; `--search`, `--application` et `--verdict` filtrent cette projection.
`node show` renvoie uniquement les identifiants publics locaux (PeerID,
`did:key`, iroh node id, custody) et ne renvoie jamais la clé privée.

Cela ne fournit pas un registre fleet. Les routes `/api/v2/nodes` de contrôle
sont des surfaces Hanko humaines ou des preuves signées par un nœud ; elles ne
sont pas une API agent pour énumérer ou usurper des nœuds. Ne tente pas
`heartbeat`, `enrollment`, `provisioning`, `register`, `mandates` ou `grants`
depuis le MCP.

## `swarm run`

Sur une connexion front door, le parcours est obligatoirement :

```text
maurice search --query <text> [--kind <kind> ...]
maurice explain <ref> [--input-file <json-file-or-stdin>]
maurice execute <ref> --input-file <json-file-or-stdin> \
  --idempotency-key <key> [--expected-plan-hash <hash>]
```

Les mêmes opérations MCP utilisent `maurice.search`, `maurice.explain` et
`maurice.execute`. Pour la CLI, `--input-file -` lit l'entrée JSON sur stdin.
`execute` exige cette entrée et une clé d'idempotence ;
le hash attendu est optionnel mais doit être conservé lorsqu'il est renvoyé
par `explain`. Lis la réponse structurée et son code : une demande hors
périmètre (`out_of_scope`), une cible absente ou un mandat manquant ne sont
pas un succès.

Sur une connexion D1, lis d’abord `inception_tasks_capabilities`, notamment
le contrat de retour épinglé. Ne transpose pas le schéma de résultat d’une
connexion front door : D1 peut exiger un autre contrat. Une exécution
`blocked` / `validation_failed` reste un échec, même si un outil runtime a
terminé. Conserve le Job et ses événements ; ne soumets pas une autre clé
pour obtenir un statut différent.

Une soumission directe utilise le contrat fermé suivant :

```json
{
  "idempotency_key": "<key>",
  "goal": "<goal>",
  "capability": {
    "agent_id": "<agent-id>",
    "workflow_id": "<workflow-id>",
    "version": "<published-version>",
    "inputs": {},
    "timeout_seconds": 300
  }
}
```

`capability` et `plan` sont exclusifs. Un plan prend la forme
`{"agent_id":"...","planner_job_id":"...","execution_plan":{...}}`.
Le délai est borné à 300 secondes. Rejouer la même clé avec la même demande
doit retrouver le même job ou graphe (`created: false`) et ne pas créer un
nouvel effet.

## `swarm jobs`

Avec un `graph_id` connu, la façade CLI publique est :

```text
maurice job graph submit --agent <agent-id> --plan <plan.json> \
  --idempotency-key <key> [--planner-job <job-id>] [--organization <org-id>] --json
maurice job graph get <graph-id> --json
maurice job graph events <graph-id> --after <sequence> --json
maurice job graph cancel <graph-id> --json
maurice job graph raise-budget <graph-id> --budget <budget.json> --json
```

`submit` exige un plan JSON valide, un Agent et une clé d'idempotence. Les
commandes de lecture renvoient le statut, les phases, les nœuds et les
révisions ; `cancel` et `raise-budget` utilisent la révision lue pour refuser
un écrasement concurrent. Les états terminaux à reconnaître sont
`completed`, `failed`, `cancelled` et `blocked`.

La route HTTP publique AgentJob possède bien une liste :

```text
GET /api/v2/applications/:applicationKey/jobs
GET /api/v2/organizations/:organizationId/applications/:applicationId/jobs
GET /api/v2/organizations/:organizationId/jobs
```

Elle est réservée aux intégrations autorisées par clé d'Application ou aux
routes humaines Hanko. `maurice swarm jobs list` existe comme projection CLI,
mais son accès humain peut exiger le principal Hanko ; le principal opérateur
local ne peut pas s'en attribuer les droits. Un refus `404` opaque ou une
absence de projection signifie que les droits manquent : n'élargis pas le
mandat et ne remplace pas ce refus par une route HTTP brute. Sans `job_id` ou
`graph_id`, signale donc la limite au lieu d'inventer une liste.

Sur D1, les équivalents sont `inception_tasks_submit`,
`inception_tasks_get` et `inception_tasks_cancel`. `get` exige exactement un
`job_id` ou un `graph_id`; `cancel` exige en plus `revision` pour un graphe.

Le groupe natif `maurice swarm jobs` expose aussi une liste bornée et paginée,
ainsi que `get` et `events` sur un Job explicite :

```text
maurice swarm jobs [--organization <org-id>] [--application <app-id>] \
  [--cursor <cursor>] [--limit <1..100>] --json
maurice swarm jobs list [--organization <org-id>] [--application <app-id>] \
  [--cursor <cursor>] [--limit <1..100>] --json
maurice swarm jobs get <job-id> [--organization <org-id>] \
  [--application <app-id>] --json
maurice swarm jobs events <job-id> [--organization <org-id>] \
  [--application <app-id>] [--cursor <cursor>] [--limit <1..100>] --json
```

La liste est une projection autorisée et paginée, pas un inventaire implicite
de toutes les organisations. Le profil `client-mcp-stdio` reprend ces
opérations avec les outils `maurice_swarm_jobs`, `maurice_swarm_job_get` et
`maurice_swarm_logs` lorsqu'il est lancé avec les droits correspondants.

## `swarm logs`

Les événements sont la lecture publique bornée de l'exécution. Ils ne sont pas
un fichier de logs arbitraire :

```text
maurice job graph events <graph-id> --after <sequence> --json
```

Pour D1, le curseur est un objet `{ "sequence": <number>, "event_id": "" }`;
la CLI le sérialise selon son contrat de page et le serveur peut le représenter
en chaîne/base64url. Réutilise exactement le curseur retourné, sans le décoder,
le fabriquer ou le remplacer par un offset inventé.

Répète l'appel avec le curseur `sequence` renvoyé et arrête-toi lorsqu'il n'y
a plus de page ou lorsque le graphe est terminal. `--follow` existe pour le
CLI, mais il s'arrête sur un état terminal ; ne l'utilise pas comme un suivi
infini et ne l'emploie pas pour prétendre lire des logs.

Sur D1, utilise `inception_tasks_events` avec soit :

```json
{"job_id":"<job-id>","cursor":{"sequence":0,"event_id":""},"limit":50}
```

soit :

```json
{"graph_id":"<graph-id>","after":0,"limit":50}
```

La limite est comprise entre 1 et 100. Les réponses renvoient le lot et le
curseur suivant ; aucun appel ne doit bloquer au-delà de ce lot.

## `start` et `stop`

Ces commandes pilotent uniquement une instance One locale :

```text
maurice start --data-dir <one-data-dir> [--server-bin <path>] [--wait <duration>] \
  [--settle <duration>] [--ready-url <url>] [--skip-ready-check] [--env KEY=VALUE] --json
maurice stop --data-dir <one-data-dir> [--timeout <duration>] --json
maurice status --data-dir <one-data-dir> --json
```

`start` renvoie notamment `pid`, `data_dir`, `ready`, `ready_checked` et
`ready_url`. Un verrou stable sans endpoint de readiness ne prouve pas que le
serveur sert effectivement des requêtes. `stop` renvoie `was_running` et le
chemin ciblé. Ne lance jamais `go run`, un serveur standalone arbitraire ou un
`kill` manuel pour compléter une intention.

Il n'existe pas d'équivalent MCP distant à `start` ou `stop`. Une connexion
front door ou D1 ne doit jamais démarrer ni arrêter un One local ou un nœud
éloigné par effet implicite.

## Reprise et erreurs

Après une interruption, reprends avec la même cible, la même référence, la
même entrée JSON, la même clé d'idempotence et le même hash de plan. Ne
soumet pas une nouvelle clé pour « vérifier » : la réponse de replay doit
retrouver le même Job ou graphe et aucun nouvel effet. Pour les événements,
reprends au dernier `sequence` ou curseur durable.

Conserve les erreurs structurées et distingue au minimum : cible absente ou
hors portée (`not_found`), conflit d'idempotence ou de révision (`conflict`),
admission refusée, mandat humain requis et indisponibilité. Une commande
acceptée, un `status` sain ou un processus démarré ne constitue pas à lui seul
une preuve de résultat métier.
