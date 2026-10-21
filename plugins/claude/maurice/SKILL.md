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

Un changement de contexte CLI ne rebranche pas le MCP déjà connecté. Invalide les références et plans observés sur l’ancienne cible. Avant une exécution sur une autre instance, vérifie son endpoint et son mandat explicites, puis refais le préflight, `search` et `explain` sur cette connexion. Si elle manque, guide le branchement public `maurice assistant connect generic --config-file <private-mcp-config> --endpoint <endpoint> --token-file <private-token-file>` ; aucun droit nouveau n’est créé et aucun fichier global n’est remplacé implicitement. Ce branchement concerne uniquement la front door. Pour External Inception / org-builder, conserve le bootstrap MCP `amb_` et la configuration renvoyée par son propre contrat ; ne les passe pas à `assistant connect` ou `agent connect`.

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

Les outils du plugin portent le préfixe `maurice_` (ou les trois noms publics
`maurice.search`, `maurice.explain`, `maurice.execute`). Les noms External
Inception restent ceux réellement publiés par le catalogue ; ne les renomme
pas côté modèle et ne fabrique jamais un outil absent.

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

## Choisir le domaine

L'invocation native est `/maurice:maurice <domaine> <commande>`. Le mot
`swarm` désigne le pilotage runtime ; `build` désigne l'authoring d'outils
AgentMaurice. Ne les confonds pas avec les commandes d'usine du domaine `dev`.

| Domaine | Commandes | Guide à lire avant l'appel |
| --- | --- | --- |
| `swarm` | `status`, `nodes`, `run`, `jobs`, `logs`, `start`, `stop` | [Swarm](references/swarm.md) |
| `build` | `new`, `check`, `plan`, `apply`, `verify`, `test` | [Build](references/build.md) |

Ces commandes sont des intentions conversationnelles. Utilise les invocateurs
publics du guide ; n'appelle pas de groupe natif `maurice swarm` ou
`maurice build` qui n'est pas présent dans l'aide du binaire. N'installe pas
une CLI lorsque la connexion MCP autorisée suffit.

Pour une commande inconnue ou une cible manquante, présente la syntaxe et
l'information requise avant tout effet. `swarm jobs` sans ID montre seulement
les Jobs observés dans la conversation, avec leur cible et date d'observation ;
pour une lecture fraîche, demande l'ID exact. Une liste conservée par le client
ne constitue pas un inventaire serveur.

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
