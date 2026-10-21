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

La création de nouveaux Agents ou Workflows, le lifecycle du swarm, les mods,
les hooks, le développement de nouveaux serveurs et la qualification Desktop
sont hors de ce plugin.
