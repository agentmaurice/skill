---
name: maurice
argument-hint: "[use <context>|doctor|swarm <command>|build <command>]"
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

Toute action qui parle à une instance Maurice, un deployment, une Application ou un Agent
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

Pour une première connexion ou « Connecte Maurice à mon One », suis le
parcours `setup` du plugin : `maurice.connection_status`, `maurice.connect`
avec l’adresse confirmée de One, puis `maurice.connection_check` après la
décision dans One. Aucun fichier à éditer, chemin privé ou secret à demander.
Sans ces outils, proposer l’installation du paquet connecté depuis le
catalogue AM ; ne pas improviser une configuration MCP manuelle.

Un changement de contexte CLI ne rebranche pas le MCP. Invalide les références
et plans de l’ancienne cible, puis vérifie la connexion explicitement choisie
avant toute nouvelle découverte. External Inception / org-builder conserve
son bootstrap `amb_`, distinct de ce parcours d’appairage front door.

## Accueil et usage

Sans domaine ni commande, affiche uniquement l’accueil et la syntaxe `swarm`
et `build`. Ne lance aucune commande CLI, aucun outil MCP ni diagnostic
spontané. Une demande explicite `doctor` ou `status` suit ensuite son propre
parcours ; son succès ne prouve ni un grant ni un résultat métier.

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
explicitement fournie par Maurice, sous la forme `/one/#/human-action/<id>`.
Ne déduis jamais cette origine, son port ou ce lien depuis le port MCP.
Si `decision` vaut `rejected`, arrête le parcours ; ne réessaie pas avec une
autre référence ou une nouvelle clé. Une carte `completed` n'est pas une
approbation et une approbation n'est pas le résultat de l'exécution.

Les outils du plugin portent le préfixe `maurice_` (ou les trois noms publics
`maurice.search`, `maurice.explain`, `maurice.execute`). Les noms External
Inception restent ceux réellement publiés par le catalogue ; ne les renomme
pas côté modèle et ne fabrique jamais un outil absent.

Le binaire CLI AGENT-1034 expose aussi les groupes natifs `maurice swarm` et
`maurice build`. Ils sont disponibles dans le code de qualification, mais
dépendent de la version installée. Lire les preuves AGENT-1034 avant de
conclure à une qualification ; la release générale reste distincte. Le profil
optionnel `maurice client-mcp-stdio` projette une liste fermée de ces commandes
locales en MCP ; il exige une configuration, un contexte et un workspace
explicitement choisis par le propriétaire. Il n'expose ni shell RPC ni
approbation et n'élargit aucun droit.

Son invocation explicite est :

```text
maurice --config <private-config> --context <context> client-mcp-stdio \
  --workspace-root <workspace> [--data-dir <instance-data-dir>] \
  [--server-bin <server-binary>] [--allow-local-write] \
  [--allow-local-lifecycle]
```

`--data-dir` et `--server-bin` sont requis avec l'opt-in lifecycle et doivent
être absolus. Le client MCP ne lit ni n'imprime de secret.

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

Le profil natif local expose aussi `maurice_doctor`, sans paramètre de requête.
Le propriétaire fixe `--data-dir`, `--health-url` et, pour le préflight MCP,
la paire `--mcp-endpoint` / `--mcp-token-file` au lancement du profil.
Ce préflight est limité au loopback ; le chemin privé ne vient jamais du modèle.
Sans cette paire, `mcp_frontdoor.checked=false` ne prouve pas un branchement.

## Choisir le domaine

L'invocation native est `/maurice:maurice <domaine> <commande>`. Le mot
`swarm` désigne le pilotage runtime ; `build` désigne l'authoring d'outils
AgentMaurice. Ne les confonds pas avec les commandes d'usine du domaine `dev`.

| Domaine | Commandes | Guide à lire avant l'appel |
| --- | --- | --- |
| `swarm` | `status`, `start`, `stop`, `nodes`, `run`, `jobs list|get|events`, `logs` | [Swarm](references/swarm.md) |
| `build` | `new module|application|agent`, `pull`, `check`, `plan`, `apply`, `test`, `verify` | [Build](references/build.md) |

Ces commandes sont des intentions conversationnelles. Utilise les invocateurs
publics du guide et vérifie l'aide du binaire réellement ciblé. N'installe pas
une CLI lorsque la connexion MCP autorisée suffit. Les interfaces nouvellement
exposées dans le backend AGENT-1034 ne sont pas encore une preuve de release
générale.

Pour une commande inconnue ou une cible manquante, présente la syntaxe et
l’information requise avant tout effet. Avec une cible autorisée, `swarm jobs`
sans ID est une lecture fraîche bornée : `maurice_swarm_jobs` dans le profil
natif ou `maurice swarm jobs list` avec le principal CLI approprié. La liste
n’exige pas d’ID. Si cette surface n’est pas autorisée, indique le refus et
sépare les Jobs déjà observés en conversation d’un inventaire serveur.

Le catalogue front door à trois verbes et le catalogue External Inception
org-builder ont des portées différentes. Vérifie les outils réellement chargés
avant de choisir le parcours. L'absence d'un outil d'authoring n'autorise ni
une route privée, ni un élargissement de mandat, ni un autre endpoint déduit.

Références canoniques du paquet : [front door](../agentmaurice/references/frontdoor.md)
et [Agent Spec V2](../agentmaurice/references/agent-spec-v2.md).

## Rapport

Pour chaque parcours, rapporte la commande ou l'outil réellement utilisé, la
cible explicite, le code de sortie, le statut structuré et la preuve obtenue.
Sépare toujours raccordement, plan, approbation, apply, verify, exécution et
qualification. Si l'interface demandée n'existe pas, indique l'invocateur
public le plus proche et le manque exact, sans fabriquer une équivalence.

Pour le préflight du profil natif, `maurice_client_context` renvoie la cible
publique validée, sans credential. Après une création d’Agent ayant déjà
initialisé sa Spec, préférer `maurice build pull` / `maurice_build_pull` à une
seconde initialisation. Un dossier vide exige `agent_id`, `agent_alias` et
`env` explicites ; le serveur fournit les fichiers et leur classification.
