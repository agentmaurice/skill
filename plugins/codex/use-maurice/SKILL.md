---
name: use-maurice
description: Utiliser la porte MCP AgentMaurice avec un mandat explicite.
---

# Utiliser Maurice

Ce skill guide l'usage de la porte MCP déjà branchée au One AgentMaurice. Il
ne démarre ni n'arrête le One et n'utilise jamais `maurice agent connect`.
Pour une première connexion ou une demande « Connecte Maurice à mon One »,
utilise le parcours `setup` livré dans le plugin : `maurice.connection_status`,
`maurice.connect`, puis `maurice.connection_check`. L’accord reste dans One.

## Parcours

1. `maurice.search` découvre les références visibles par le mandat courant.
2. `maurice.explain` confirme la cible exacte, les schémas, la politique, le
   `plan_hash` et les effets attendus.
3. `maurice.execute` est réservé à la référence expliquée. Il reçoit la même
   cible explicite, une entrée validée, une `idempotency_key` et, lorsque le
   plan est lié, le `expected_plan_hash`.

Ne déduis jamais un Agent, une Application, un Workflow, une version ou une
identité depuis un nom d'affichage. Conserve la référence complète retournée
par `search` et la cible du One choisie par l'utilisateur.

Une réponse `pending` ou une demande d'approbation reste en attente : utilise
`explain` sur la référence `pending_action:<id>` pour observer l'état et
présente la surface humaine indiquée par la réponse. Ne clique pas, ne
réponds pas et ne simule jamais la décision humaine. Une révocation, une
expiration, un refus ou un conflit d'idempotence bloque le parcours ; ne
réessaie pas avec une autre cible ou une nouvelle clé pour contourner l'état.

Pour présenter la carte, consulte le [contrat front door](../agentmaurice/references/frontdoor.md). Utilise le lien retourné par le serveur, ou le chemin documenté `/one/#/human-action/<action_id>` sous l’origine de l’instance explicitement fournie par l’utilisateur. Ne déduis jamais le port API depuis le port MCP. Sans origine connue, demande le lien de l’accueil humain du One ; ne fabrique pas une URL et ne lance pas de viewer CLI.

Lis toujours `structured_content` lorsqu'il est présent, même si le bloc
`content[].text` est vide. Dans une réponse de carte, `status: "completed"`
signifie seulement que la carte a été résolue ; lis séparément
`decision: "approved"` ou `decision: "rejected"`. Une décision rejetée arrête
le parcours : ne réessaie pas, ne crée pas de nouvelle clé et ne transforme
jamais le statut de la carte en réussite métier. N'annonce une réussite
fonctionnelle qu'après le résultat de l'opération autorisée, pas depuis le
statut de la carte. Ne parse aucun fichier de configuration ni aucun jeton.

Si la connexion manque, utilise les outils de connexion du paquet publié.
Demande seulement l’adresse de One, présente le lien et le code retournés,
puis attends la décision de la personne. Ne demande jamais un chemin privé,
un fichier de configuration ou un jeton. Si ces outils ne sont pas chargés,
indique que le paquet connecté doit être installé depuis le catalogue AM.

L'approbation humaine reste distincte du mandat de l'assistant. Ne demande
jamais de secret dans le chat, ne copie pas de jeton dans un fichier partagé,
et n'auto-approuve aucune opération.
