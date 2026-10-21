# Commandes Claude swarm et build — AGENT-1034

Qualification du 21 octobre 2026, en complément de
[la première campagne Claude](AGENT-1034-claude.md).
**Les parcours des commandes sont complétés sur les interfaces publiques
existantes ; le lot complet reste In Progress.** La parité CLI/MCP universelle
PLUG-12 et le rejeu Desktop ne sont pas déclarés acquis.

## Paquet et périmètre

Le routeur natif `/maurice:maurice` charge une référence dédiée à chaque
domaine. Le builder embarque désormais ces références et vérifie leurs liens.
La Skill canonique reste copiée octet pour octet ; l'archive Codex reste
inchangée. Aucun mod, hook, gateway, réglage global ou groupe natif CLI
`maurice swarm` / `maurice build` n'est ajouté.

- Claude Code **2.1.299**, modèle **claude-sonnet-5-5**, dans nos propres
  shells internes. Aucune session existante reprise ou réglage Claude global
  modifié. Le One isolé est `agent-1034`, backend propre
  `4fd020849d7fa52361d371bd5dfbfceb48991e3c`.
- **26 conversations guidées conservées dans la preuve**, avec permissions de session bornées aux
  commandes littérales ou aux outils MCP nécessaires. Ce sont des rejeux
  fonctionnels dans le client réel, pas un benchmark de routage autonome.
- **21 tests réussis**, validation native stricte réussie, pas de hook.
  Les tests de packaging vérifient maintenant aussi la copie de tous les
  guides et la résolution de leurs liens à l'intérieur du paquet.
- Archive finale SHA256 : `2972c5fee9e2f947795f40ccaaf71399d61397d4646120fd9aad860f6d85ea6e`.
- Skill canonique 2.0.39 :
  `ef85a08bc3e34b153e1db7667524326c53e2701b11c10d1b2a5f2473508eb96d`.

La [preuve JSON](AGENT-1034-commands.json) conserve les appels et réponses
structurées, les erreurs, les identifiants, les hashes des transcripts et des
archives utilisées par chaque itération. Les derniers rejeux verify CLI/MCP
et reprise D1 utilisent l'archive finale. Les credentials restent dans les
fichiers privés de qualification et n'entrent jamais dans le paquet ou la
preuve publiée. Les réponses de schémas volumineuses sont représentées par
leur identité et leur digest.

## Matrice réellement rejouée

| Intention | Interface et constat |
| --- | --- |
| `swarm status` | CLI `status --data-dir` : `running=true` sur le seul One du ticket. |
| `swarm nodes` | CLI `node show --data-dir` : PeerID, did:key, iroh_node_id et custody publics. Cette preuve porte sur l'identité locale ; la projection personnelle `access list --me` reste guidée, sans preuve Hanko dans cette campagne. |
| `swarm run` | Front door déjà qualifiée dans la campagne initiale ; D1 `capabilities → submit` de `job-proof@1`, résultat `{ok:true}` conforme au contrat épinglé. |
| `swarm jobs` | D1 `get` : Job `dbccvm24p5cu03m63f1g` completed, une tentative, résultat typé et validé. |
| `swarm logs` | D1 `events`, limite 50 : 10 événements jusqu'à `job.completed`, curseur sequence 10. Aucun suivi infini ou fichier de logs arbitraire. |
| `swarm stop` / `swarm start` | CLI avec le même `--data-dir` : was_running=true, puis ready=true/ready_checked=true et running=true au nouveau PID. |
| `build new Module` | Scaffold `qualification-1034`, validation et module test réussis. Ce test contrôle le manifeste ; il n'exécute pas de Workflow. |
| `build new Application` | Application fictive `qualification-1034-commands` créée, ID `dbccm4i4p5cs00tc0mi0`. Les préparations ultérieures de sa surface et de sa clé D1 restent des opérations explicites de fixture. |
| `build new Agent` | Observation, plan create_agent, autorisation policy:integration_test, apply et vérification du graphe via le dispatch MCP. Agent `dbcd1ca4p5cu03m63gkg` créé une fois, état draft. Le handoff retourne authoring_required (instance_url absent dans cette fixture) ; le scaffold explicite CLI du même Agent crée ensuite la Spec initiale `dbcd2oi4p5cu03m63glg`, sans Workflow ni déploiement. |
| `build check` | Lecture du projet puis CLI check : contrats valides, ok=true, test plan déclaré. |
| `build plan` | Nouveau plan immuable avec hash, diff, provenance et policy. Aucune décision humaine fabriquée. |
| `build apply` | Plan `dbccnea4p5cs00tc0nag` autorisé par policy, apply avec tests auto ; 1 cas réussi, test run `dbcco7q4p5cs00tc0o10`. |
| `build verify` | Même plan courant `dbccteq4p5ckv9ujcb0g` relu par CLI et MCP : même hash, verified=true, drift=false, même rapport de tests. |
| `build test` | Nouveau plan `dbccrt24p5ckv9ujc6rg`, desired state inchangé, vrai nouveau run `dbccsqq4p5ckv9ujca6g` (1/1 passé). Replay du même plan/clé : replayed=true et même run ; aucun nouveau test déclenché. |

## Reprise et erreurs conservées

Une nouvelle conversation Claude reprend le Job D1 avec la requête exacte :
`created=false`, même Job completed, même résultat et mêmes événements. Le
contrôle indépendant du One constate **3 AgentJobs** : le Job front door
initial, le Job D1 bloqué et le Job D1 terminé. Le fichier de preuve initial
est inchangé. Les effets du nouveau Job D1 sont une lecture locale, avec
zéro appel LLM côté One ; les vrais modèles clients ont bien été sollicités.

Les premiers essais ne sont pas comptés comme des réussites : listing shell
hors permission, header de bootstrap mal assemblé, dispatch lazy non autorisé
et plan stale à cause du lock ancien. Les corrections sont limitées aux
permissions de la fixture, au header privé et au guidage public. La reprise
stale passe par `spec pull`, revue et commit, puis nouveau plan ; aucun lock
n'est réécrit manuellement et aucune clé d'idempotence n'est changée pour
contourner un plan terminal.

Le premier Workflow D1 `list-proof` renvoyait `{listed:true}` alors que le
contrat D1 exige `{ok:true}` : Job `dbccq5q4p5ckv9ujbt60` bloqué avec
validation_failed, correctement rapporté et conservé. Une nouvelle capacité
fictive `job-proof`, publiée par Agent Spec, sert au cas nominal. Il s'agit
d'un autre Workflow et d'une autre opération, pas du retry déguisé du Job
bloqué. Le guide impose désormais la lecture du contrat de retour D1 et ne
transpose pas implicitement le contrat de la front door.

Le builder MCP utilise ici un catalogue à chargement différé :
`inception_search({tool_name})`, puis
`inception_call({tool_name, arguments})`. Le guide couvre ce dispatch réel
ainsi que les catalogues qui exposent directement les noms. Le bootstrap
MCP d'authoring est distinct de `assistant connect` pour la front door.

## Dépendances et limites restantes

La consommation MCP déjà appairée n'impose pas MauriceCLI. Dans cette
campagne, la CLI reste nécessaire pour le bridge stdio front door initial,
les opérations locales (identité, start/stop, fichiers Module/Agent Spec) et
les parcours Git-native explicitement choisis. D1 et le builder ont été
appelés en HTTP MCP natif par Claude, sans nouveau bridge ou gateway.

Les limites de produit ne sont pas masquées par le guidage :

- `nodes` ne livre pas un inventaire générique fleet/pairs/grants ; les
  projections publiques ont leur portée et leurs principals respectifs.
- Le CLI sait lire les graphes, D1 les Jobs et graphes ; aucun `job list/logs`
  natif supplémentaire n'est créé. L'absence d'ID n'est jamais une liste vide
  prouvée : le client demande la cible/ID ou montre ses seules observations
  datées.
- Le lifecycle et le scaffold local n'ont pas d'équivalent MCP distant.
  PLUG-12 pour toutes les commandes reste donc un écart de contrat, même si
  les parcours du plugin fonctionnent dans leurs surfaces disponibles.
- Le nouvel Agent est un draft avec scaffold ; le handoff Studio automatique
  n'est pas qualifié. Aucun Agent métier ou modèle n'est déclaré déployé.
- Desktop Code, reprise d'approbation humaine dans Claude, changement de cible
  et incompatibilité de protocole restent hors des preuves de cette campagne.
  La consigne du fondateur est de préserver ses sessions et d'utiliser notre
  shell CLI.
- Les domaines mod/dev restent AGENT-1035/1036/1037. Aucune publication
  marketplace, release binaire ou opération de production n'est faite.

Le ticket reste **In Progress**, la PR **Draft**, sans auto-merge. Ces limites
interdisent de présenter le lot AGENT-1034 complet comme clôturé.
