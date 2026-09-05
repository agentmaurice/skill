# AGENTS.md — agent-maurice-skill

Instructions pour tout agent de code (OpenAI Codex, Claude Code, Cursor,
Gemini ou autre) qui travaille dans ce dépôt. Codex lit ce fichier depuis la
racine Git ; Claude Code le charge par la ligne `@AGENTS.md` de `CLAUDE.md`.

## Rôle du dépôt

Skill public pour agents de code (rail Agent Spec V2).
Article de référence : `wiki/projects/agent-maurice-skill.md` dans pilote-maurice.

<!-- agentmaurice:common:start -->
## Socle commun AgentMaurice

Bloc synchronisé depuis `pilote-maurice/workspace/AGENTS-common.md`
(dépôt `mcpchatui/pilote-maurice`, branche `main`) ; ne pas l'éditer dans un
autre dépôt. Contrôle : `python3 scripts/agents_sync.py --check` depuis
pilote-maurice.

**Où sont les règles.** Le wiki et la gouvernance vivent dans le dépôt
pilote-maurice : `wiki/INDEX.md` (navigation, commencer ici pour toute
question ou tâche AgentMaurice), `wiki/SCHEMA.md` (autorité des sources,
statuts des articles, modes de travail), `wiki/operations/agent-coding-guidelines.md`
(règles d'édition, cycle Plane/Git, gates), `wiki/design/interface-principles.md`
(interfaces, selon le profil de la surface), `wiki/naming-conventions.md` et
`wiki/glossaire-technique-marketing.md` (vocabulaire externe),
`wiki/architecture/auth-security.md` (authentification cible ; ne pas
l'inférer du code legacy). Citer les articles utilisés.

**Trouver pilote-maurice depuis ce checkout**, dans l'ordre : 1) le
répertoire `$AGENTMAURICE_PILOTE_DIR` s'il est défini ; 2) `../pilote-maurice`
à côté de la racine Git de ce dépôt (workspace parent) ; 3) pour un worktree,
le voisin `pilote-maurice` du checkout principal (première ligne de
`git worktree list`) ; 4) sinon, cloner `git@gitlab.com:mcpchatui/pilote-maurice.git`
hors de ce dépôt et exporter la variable. Ne jamais retenir une copie située
sous `_archive/` ou `_worktrees/`. Diagnostic et preuve :
`python3 <pilote-maurice>/scripts/agent_bootstrap.py`.

**Règles impératives.**

- Logiciel propriétaire : ni open source, ni open core. Français par défaut,
  termes techniques en anglais. L'identifiant interne interdit (périmètre dans
  `wiki/SCHEMA.md`) n'apparaît jamais dans un contenu produit ou public.
- Wiki-first est un ordre de navigation, pas une priorité de vérité : un écart
  entre contrat, wiki et code se signale explicitement, il ne se tranche pas
  en silence.
- Une question, une revue ou un diagnostic ne modifie aucun fichier.
- Une spec pure s'écrit d'abord dans le wiki (article + `INDEX.md` + `LOG.md`
  + lint), sans fiche Plane préalable ni passage `In Progress` ; le ticket
  d'implémentation est créé ensuite, au `Backlog`.
- Une implémentation (code, configuration, infrastructure) exige une fiche
  Plane `In Progress`, puis `task work:start TICKET=AGENT-N PLANE_ID=<uuid>`
  depuis pilote-maurice avant toute branche ; ensuite `work:checkpoint`,
  `work:submit` et `work:closeout` avec les mêmes identifiants. Sans accès
  Plane, ne pas démarrer le chantier.
- Ne jamais éditer `_archive/`. Ne jamais annoncer « terminé » ou « tests
  OK » sans la vérification correspondante.
- Un changement d'interface ou de parcours utilisateur est rejoué dans
  l'interface réellement exécutable, ou déclaré explicitement non vérifié.
- Release produit/BOM : `task release:local` depuis la racine du workspace
  (runbook `wiki/operations/local-release-gate.md`).
- Outils de graphe de code (MCP `code-review-graph`) : les utiliser d'abord
  quand ils sont disponibles ; s'ils sont absents, en erreur ou incomplets,
  revenir à Grep/Glob/Read et le dire dans le compte rendu.
<!-- agentmaurice:common:end -->

## Sources à lire selon la tâche

| Tâche | Lire d'abord (dans pilote-maurice) |
|-------|-----------------------------------|
| Comprendre le dépôt avant d'éditer | `wiki/INDEX.md` puis `wiki/projects/agent-maurice-skill.md` |
| Règles d'édition, cycle Plane/Git, gates | `wiki/operations/agent-coding-guidelines.md` |
| Tests, stabilité, release | `wiki/operations/testing.md`, `wiki/operations/stability-strategy.md`, `wiki/operations/local-release-gate.md` |
| Interface ou parcours utilisateur | `wiki/design/interface-principles.md` (profil de la surface) |

## Commandes locales et vérifications

Aucun fichier de build à la racine : lire le `README.md` et le pipeline du dépôt ; ne pas inventer de commande.
