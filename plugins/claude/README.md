# Maurice

Plugin Claude privé pour utiliser AgentMaurice avec le MCP déjà configuré.

Le plugin expose le skill `maurice` dans le namespace Claude
`/maurice:maurice`. Il réutilise la connexion MCP existante et le mandat déjà
accordé ; il ne contient ni serveur MCP, ni hook, ni credential, ni fichier de
configuration de machine.

Pour une session isolée, construire puis charger le plugin avec la commande
explicite documentée dans le dépôt :

```bash
python3 scripts/build_client_plugin.py --client claude --output <output>
claude --plugin-dir <output>/plugins/maurice
```

Le skill guide `search`, `explain` et `execute` avec une référence exacte, un
plan hashé et une clé d'idempotence. Les cartes humaines restent dans leur
surface d'approbation ; le plugin ne les approuve pas.

Les domaines `swarm` et `build` guident les commandes publiques existantes :
lifecycle local à cible explicite, exécution gouvernée et rail Agent Spec. Le
backend de qualification AGENT-1034 expose en plus les groupes natifs
`maurice swarm` et `maurice build`, encore à qualifier live avant une release
générale. Le profil optionnel `maurice client-mcp-stdio` projette un sous-ensemble
fermé de commandes CLI locales après choix explicite de `--config`, `--context`
et `--workspace-root`; `--data-dir` et `--server-bin` sont explicites pour le
lifecycle. Ses droits d'écriture et de lifecycle sont opt-in.
Il n'installe pas MauriceCLI et ne démarre aucun service automatiquement.
Les mods, hooks et le domaine `dev` appartiennent aux lots suivants. La
qualification Desktop reste distincte du test terminal.
