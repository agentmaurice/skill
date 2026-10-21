# Qualification terminal du plugin Claude — AGENT-1034

État au 21 octobre 2026 : **implémentation en cours, lot complet non clôturé**.
Le paquet `maurice 0.1.0` est construit et utilisé dans de vraies conversations
Claude Code. Le rejeu dans l’onglet Code Desktop est différé : le fondateur a
signalé des travaux actifs et demandé d’utiliser la CLI dans notre propre shell.
Aucune session existante n’a été pilotée et aucun réglage global édité pour ce test.

## Livrable et versions

Le même builder produit désormais `--client codex` ou `--client claude`. Le paquet
Claude possède `.claude-plugin/plugin.json`, un README, le Skill canonique dans
`skills/agentmaurice` et son guide dans `skills/maurice`. Son invocation native
est `/maurice:maurice`, suivie des intentions `use`, `doctor`, `swarm` ou `build`.
Ce sont des intentions guidées, pas de nouveaux groupes exécutables MauriceCLI.
Aucun mod, hook, nouveau serveur MCP ou identifiant de poste n’est embarqué.

- macOS 27.0.1 (26A434) ; Claude Code **2.1.299**, modèle **claude-sonnet-5-5**.
- Codex CLI **0.163.0**, modèle **gpt-6.1-sol**, pour le rejeu croisé.
- One natif isolé `agent-1034`, backend **4fd020849d7fa52361d371bd5dfbfceb48991e3c**,
  build de développement `plugin-qualification-4fd02084`.
- Skill canonique **2.0.39**, copié octet pour octet. Empreintes exactes dans
  [la preuve JSON](AGENT-1034-claude.json). L’archive Codex reste identique
  à celle qualifiée par AGENT-613.
- Deux mandats fictifs : exécuteur borné à cinq effets et lecteur d’un seul
  Workflow. Tokens privés consommés par le bridge CLI existant, jamais copiés
  dans le paquet, les prompts ou cette preuve.

## Parcours réellement rejoués

| Parcours | Résultat observé |
| --- | --- |
| Installation session | Chargement `--plugin-dir`, plugin `maurice@inline` et Skills `maurice:maurice` / `maurice:agentmaurice` présents dans le client réel. |
| Sans mod | Aucun hook dans le paquet ; `one-bridge` absent des plugins chargés. Les plugins internes Claude restent ceux du client. |
| Accueil sans domaine | Aucun appel métier, aucune CLI, aucun `execute`. |
| `swarm run` via MCP | Recherche, schéma/plan et exécution du Workflow publié `record-proof` ; écriture puis relecture de « Preuve commune Codex Claude » dans `/qualification/shared-client.txt`. |
| Parité Claude / Codex / CLI | Même ref, entrée, clé `agent-1034-shared-client-1`, plan, Job `dbcc1ka4p5cken7sk05g`, exécution `cks7p63rtpgt621ls8j0` et résultat `recorded=true`. |
| Reprise après redémarrage | Arrêt/démarrage natif du seul One du ticket ; nouvelle conversation Claude au même ref/input/key/hash, mêmes Job/exécution, aucun nouvel effet. |
| Lecteur sans exécution | Découverte/explanation autorisées ; `execute` refusé `out_of_scope`, sans nouveau Job ni fichier. |
| Mandat révoqué | Révocation par la CLI d’opérateur du test ; nouveau client Claude avec MCP `failed`, pas de faux succès ni reconnexion/création de droit. |
| Connexion absente | Plugin chargé, catalogue MCP vide : diagnostic « aucune connexion », sans déduire un succès de l’installation. |
| `swarm status` local | Commande native exacte avec `--config` et `--data-dir` du ticket exécutée par Claude : `running=true`. Cela ne qualifie pas l’inventaire d’un swarm. |
| `build check` | Commande native exacte sur le projet fictif : `agentmaurice.agent_spec_check/v2`, `ok=true`, contrats valides, hash de Spec. Aucun plan ou apply déclenché. |

Au contrôle final, SQLite contient **un Agent Job**, l’exécution est terminée,
le fichier attendu contient les octets convenus et le fichier du lecteur est
absent. Le zéro coût qualifié concerne les outils locaux du One ; les modèles
réels des clients ont bien été sollicités.

Les sessions Claude utilisent `--restricted`, `--strict-mcp-config`, un plugin
explicite et `--no-session-persistence`. Les outils MCP sont autorisés seulement
sur la connexion fictive du ticket. Les deux tests CLI ont une permission de
session limitée à leur commande exacte ; aucune permission globale ou carte AM
n’est approuvée. Les premiers essais CLI avaient été refusés avant exécution
(permission trop étroite / commande composée avec un `echo`) ; ils restent
conservés dans la preuve et ne sont pas comptés comme réussis. Les commandes
seules ont ensuite été réellement exécutées.

## Contrôles du paquet

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
python3 scripts/build_client_plugin.py --client claude --output <sortie-vide>
claude plugin validate --strict --json <sortie-vide>/plugins/maurice
```

**21 tests réussis**, validation native stricte réussie, aucune erreur de
manifeste et aucun hook. Le validator signale encore l’absence d’icône de
listing ; la publication marketplace n’appartient pas à cette qualification.
Les tests couvrent aussi la parité du Skill, la reproductibilité, les liens
symboliques et le refus des sorties invalides. La lecture du code a commencé
par `ripwire . --query='build client plugin archive canonical skill marketplace'
--top-k=8 --max-tokens=1800`, puis une revue indépendante et les aides CLI réelles.

## Reste nécessaire avant clôture du lot complet

| Critère / surface | Manque précis |
| --- | --- |
| PLUG-10 Desktop Code | Rejeu réel à effectuer dans une session de qualification libre, sans modifier les travaux actifs du fondateur. |
| PLUG-12 toutes commandes | La parité stricte est prouvée pour le parcours front door. Elle ne l’est pas pour chaque intention `nodes`, `jobs`, `logs`, lifecycle et authoring. |
| Inventaire de nœuds | Le guide expose `access list --me` et l’identité locale `node show` ; cela n’est pas une façade générique CLI/MCP d’inventaire du swarm. Ne pas remplacer ce manque par des routes privées ou un nouvel adaptateur non contracté. |
| Jobs / logs | Guidage vers `job graph get/events` ou `inception_tasks_get/events` avec ID explicite. Aucune commande `job list/logs` nouvelle ni connexion Inception qualifiée dans ce profil front door à trois verbes. |
| Lifecycle et build complet | Start/stop et déploiement de la fixture ont été exercés par l’opérateur de qualification ; leur guidage conversationnel complet, `new`, `plan`, `apply`, `verify` et `test` n’est pas qualifié ici. |
| PLUG-07/08 et erreurs restantes | Rejeu Claude d’attente/décision humaine, changement de cible et incompatibilité de protocole encore à effectuer. La preuve Codex AGENT-613 ne remplace pas ces tests Claude. |

Les commandes indiquées par le guide sont confrontées au code et aux aides
publiques, avec leurs limites. Leur présence documentaire ne démontre pas un
rejeu client. Aucun groupe natif `maurice swarm` ou `maurice build` n’est livré
par ce paquet. `spec init` prépare un Agent existant ; il ne crée pas un Agent.
Le domaine `dev` (AGENT-1036, outils AGENT-1037) et le mod (AGENT-1035) restent
séparés. La validation du paquet ne vaut ni qualification Desktop, ni release
One, ni publication publique. Le ticket reste In Progress et sa PR reste Draft.
