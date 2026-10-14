# AGENTS.md — agent-maurice-skill

Instructions pour tout agent de code (OpenAI Codex, Claude Code, Cursor,
Gemini ou autre) qui travaille dans ce dépôt. Codex lit ce fichier depuis la
racine Git ; Claude Code le charge par la ligne `@AGENTS.md` de `CLAUDE.md`.

## Rôle du dépôt

Skill public pour agents de code (rail Agent Spec V2).
Article de référence : `wiki/projects/agent-maurice-skill.md` dans pilote-maurice.

<!-- agentmaurice:common:start -->
## Socle commun AgentMaurice

Bloc synchronisé depuis `pilote-maurice/workspace/AGENTS-common.md`. Ne pas l'éditer dans un autre dépôt. Contrôle : `python3 scripts/agents_sync.py --check` depuis pilote-maurice. Le détail est dans `wiki/operations/usine-logicielle.md` et `wiki/operations/agent-coding-guidelines.md`, lus à la demande.

**Invariants.** Logiciel propriétaire, ni open source ni open core. Français, termes techniques en anglais. L'identifiant interne interdit (`wiki/SCHEMA.md`) n'apparaît pas dans un contenu public. Une question ne modifie aucun fichier. Ne jamais éditer `_archive/`. On n'annonce « terminé » ou « tests OK » qu'après la vérification.

**Cycle et preuve.** `WORKFLOW.md` à la racine de chatserver, de l'OS et de la Console.

**Carte de code.** Si `ripwire` est dans le `PATH`, l'utiliser d'abord (`wiki/operations/ripwire-code-context.md`). Sinon le MCP `code-review-graph`. S'ils manquent, Grep, Glob ou Read. Vérifiable, sous-agents compris : le compte rendu cite la commande ripwire, ou porte la mention « graphe indisponible, exploration par lecture ».

**Release.** `task release:local` depuis la racine du workspace (`wiki/operations/local-release-gate.md`). Ce n'est pas le cycle d'une feature.

**Navigation.** `wiki/INDEX.md`, puis l'article du sujet.
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
