# Qualification locale du plugin Codex — AGENT-613

Qualification du 21 octobre 2026, sur données fictives. Le paquet privé est
`maurice 0.1.0`. Cette preuve couvre le client Codex CLI ; elle ne qualifie
pas séparément l’interface Codex Desktop ni une publication marketplace.

## Versions et périmètre

- macOS 27.0.1, build 26A434 ; `codex-cli 0.163.0` ; modèle `gpt-6.1-sol`.
- One natif isolé, version de développement `plugin-qualification-4fd02084`,
  construit depuis chatserver `4fd020849d7fa52361d371bd5dfbfceb48991e3c`.
- Skill canonique 2.0.39, copié sans modification. Les empreintes exactes du
  Skill, du guide runtime et de l’archive sont dans [la preuve JSON](AGENT-613-codex.json).
- Profil Codex, configuration, mandats, stockage, SQLite et NATS dédiés au
  ticket. Aucun provider LLM AM ni compte Console ajouté. Le modèle réel est
  celui du client Codex authentifié.
- Deux mandats : exécution bornée à cinq effets sur les ressources fictives ;
  lecture seule limitée à un seul Workflow. Aucun jeton dans le paquet ou la preuve.

## Résultats observés

| Critère | Preuve |
| --- | --- |
| CODEX-01 | Build reproductible, manifeste portable et overlay `.codex-plugin`, archive inspectée, parité binaire du Skill canonique ; installation réelle privée réussie. |
| CODEX-02 | Préflight authentifié ; branchement généré idempotent octet pour octet ; entrée tierce conservée ; conflit et mandat révoqué refusés sans modification du fichier. Doctor `mcp_frontdoor.checked=true`, `ok=true`. |
| CODEX-03 | Vraie conversation depuis une demande métier : chargement du Skill, `search`, `explain`, `execute`, écriture puis relecture par deux tool calls réels. Résultat `recorded=true`, contenu vérifié dans le stockage. |
| CODEX-04 | Nouvelle conversation après arrêt/démarrage natif du One : même clé, même Job `dbcb83a4p5cn1ijqabt0`, même exécution `mr5r41acogtsdj3tvc10`, même fichier. Aucun second effet. |
| CODEX-05 | Attente avant démarrage puis avant écriture, décisions effectuées par le fondateur dans l’interface One existante ; reprise avec même entrée/clé/plan, Job `dbcbcoi4p5cn9l46j3u0`, exécution `u83a5ahl3o7ro714to3g`, résultat métier relu. Autre demande refusée par le fondateur : observation `rejected`, arrêt sans réessai, fichier absent. Lien humain rendu depuis une origine explicitement fournie. |
| CODEX-06 | Catalogue de trois Workflows pour l’exécuteur, un pour le lecteur ; exécution du lecteur et référence hors portée refusées `out_of_scope` ; révocation effective, catalogue inaccessible et aucun effet supplémentaire. |
| CODEX-07 | Accueil réel sans appel à `execute` ; aucun mod, hook ou outil d’usine. Les invocateurs réellement livrés sont documentés dans [l’installation](../install.md). |
| CODEX-08 | Versions et portée ci-dessus ; résultats, décisions, identifiants, compteurs et hashes des transcriptions dans la preuve JSON. |

Au contrôle final : deux Agent Jobs au total, deux exécutions terminées et deux
fichiers attendus. Les fichiers du lecteur et du parcours refusé sont absents.
Les contrôles de portée et de connexion utilisent la CLI publique ; les parcours
métier, reprise, attente, refus et accueil passent par de vraies conversations Codex.

## Corrections issues du client réel

Le manifeste portable seul ne s’installait pas dans ce build Codex ; l’overlay
`.codex-plugin/plugin.json` a été ajouté et l’installation rejouée. Une première
restitution du refus par le modèle était incorrecte malgré une réponse serveur
structurée correcte : le guide distingue désormais le texte vide, les données
structurées, le statut de carte et sa décision. Le refus et les reprises ont
été rejoués après correction ; la première tentative reste conservée dans la preuve.

La configuration YAML du lanceur natif ne projetait pas la qualification de coût
Agent Jobs. Le One de test a donc été relancé avec la variable serveur documentée
`AGENT_JOBS_ZERO_COST_TOOLS`, limitée aux trois outils de stockage locaux et au
hash exact de la Spec vérifiée. Aucun changement de politique ou de code backend.

## Reproduction et limites

```bash
python3 scripts/build_client_plugin.py --client codex --output <repertoire-vide>
CODEX_HOME=<profil-isole> codex plugin marketplace add <repertoire-vide>
CODEX_HOME=<profil-isole> codex plugin add maurice@maurice-local
python3 -m unittest discover -s tests -v
```

Le test réel nécessite un One déjà démarré, des Workflows fictifs vérifiés, un
mandat existant, un fichier de jeton privé et un modèle Codex authentifié. Les
approbations des trois outils MCP dans le profil de qualification ne décident
jamais les cartes humaines AM. Le serveur renvoie une référence d’action ;
l’origine de la page humaine doit être explicitement connue pour rendre le lien.
Aucun port API n’est déduit du port MCP. Les assets de la page humaine existante
ont été utilisés seulement pour les décisions du fondateur ; aucune qualification
générale du Viewer ou d’une release One n’en est déduite.

Le contexte public de MauriceCLI, Claude Code, ChatGPT distant, les domaines
`swarm`/`build`/`dev`, le mod et la publication sont hors de cette preuve.
La qualification backend locale ne démontre pas une disponibilité dans un binaire publié.

La gouvernance a conservé les contrôles Git/Plane et l’isolation ; seule la
capacité WIP a fait l’objet de la dérogation explicite du fondateur, pour traiter
AGENT-613 puis AGENT-1034 en séquence. Exploration par `ripwire` puis lectures
ciblées : `ripwire <checkout-backend> <checkout-skill> --top-k=120 --max-tokens=14000`.
