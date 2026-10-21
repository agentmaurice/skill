# Interfaces natives CLI/MCP et révocation — AGENT-1034

Qualification locale du 21 octobre 2026, backend `chatserver`
`0df11b39c716d710ed01fd405db2a4da90b0294f`, One isolé
`agent-1034-interfaces` (API 43700, front door 43731, sans OS).
Les nouvelles sessions Claude sont des sous-processus du shell interne ; les
sessions utilisateur et les autres One ne sont pas utilisés.

## Paquet de guides final

L’archive finale après clarification des guides a le SHA-256
`c14728298a9ec8a46701bd19fbe1822e20a64c6faa74c234f09c61e815cb699e`.
Les références à `6d112a…` ci-dessous décrivent le paquet précédent et restent
historiques. Les guides finaux corrigent la liste fraîche de Jobs, les alias
racine, le profil MCP de lifecycle et le sens explicite du résultat de test
rejoué. L’accueil sans domaine ne lance désormais aucune commande ni outil MCP.

Les trois parcours accueil, lifecycle et build sont rejoués dans de nouveaux
Claude CLI sur cette archive finale. Le build retrouve une preuve PASSED
existante, avec `replayed=true`, puis verify sans dérive ; il ne prétend pas
avoir relancé les tests. Les 21 selftests du dépôt, dont 4 consacrés au
packaging, passent ; le validateur natif Claude passe également.

La PR du plugin reste Draft : la qualification de l’onglet Code de Claude
Desktop du critère historique PLUG-10 n’est pas effectuée par cette campagne
shell. Les constats de la revue client restent traçables, avec leurs limites
historiques et la clarification ultérieure des guides ; ils ne constituent
pas un reçu accepté au HEAD final. Aucun closeout du ticket n’est revendiqué.
Le reçu One commun au HEAD final est généré après ce commit et joint aux PR.

## État final après relecture adverse

Le backend final est `fb0b0d679d01dd81ce94fa9e8a984d2833d80971`, à jour de
`main` (`69f34c96`). Les éléments ci-dessous au commit `0df11b39` restent
historiques ; les nouveaux parcours réels sont aussi rejoués au HEAD final.

La relecture adverse utilise un nouveau Claude CLI Anthropic, avec uniquement
le diff et les critères Plane. Son [reçu et les résolutions](AGENT-1034-adverse-review.json)
conservent tous les constats. Le validateur de gouvernance courant confirme
zéro bloquant ouvert, sans exemption. Seul le test de résolution a changé après
la revue, conformément au contrat officiel de reçu.

Les défauts réels corrigés sont le filtre d’organisation après pagination de
`swarm nodes`, la course de cible entre snapshot et première sonde, les entrées
Job/curseur invalides et les limites HTTP non numériques. Les filtres nodes
existent aussi en MCP ; les alias racine `job list/get/events` sont qualifiés
contre `maurice_swarm_jobs/job_get/logs`. L’ancien curseur HTTP à séquence seule
reste compatible. Le scaffold invalide ne crée aucun dossier, le manifeste
partiel est retiré sur erreur et le diagnostic MCP comporte du texte lisible.
La régression de course utilise un exécutable Go, sans dépendance Python.

La suite courte CLI/API/frontdoor/controllers et les tests complémentaires
passent. Un nouveau plan partagé et son test PASSED 1/1, apply rejoué et verify
sans dérive sont vérifiés sur le backend final. Une nouvelle lecture fictive
front door est `completed`, avec un outil, zéro LLM et quota1 après les rejeux.
Le lifecycle est de nouveau qualifié par Claude CLI : arrêt puis démarrage du
seul runtime de test, running et ready. Les identifiants finaux sont dans le
rapport JSON, sous `post_review`.

Les réfutations documentées distinguent le nom historique du runtime et ses
identifiants internes des domaines du plugin ; le résultat de test rejoué est
explicitement marqué et ne prétend pas relancer un test ; les autorités MCP
locale et front door restent distinctes. Le même résultat métier est vérifié
avec le même grant, pas en élargissant un credential.

La qualification Hanko historique garde son état expiré après délai, distinct
du Workflow front door terminé. Le profil local exige un contexte lié à une
organisation ; les copies privées de configuration sont supprimées à la fin
normale de la session. Un arrêt brutal reste une limite de nettoyage locale,
pas une qualification d’isolation OS. Aucun replay Claude Desktop ni release
n’est revendiqué. La fiche reste In Progress jusqu’au closeout gouverné.

## Livré et vérifié

- CLI `swarm status|start|stop|nodes|run|jobs|logs`, lectures `job list|get|events`.
  Les enveloppes publiques Job/actions/provenance/approvals et les champs
  additionnels sont conservés. Les événements acceptent une limite 1–100 et
  leur curseur `{sequence,event_id}`, en chaîne JSON ou base64url.
- CLI `build new module|application|agent`, `pull|check|plan|apply|test|verify`.
  `new agent` initialise la Spec d’un Agent existant. Si elle existe déjà,
  `pull` amorce le projet avec Agent, alias et environnement explicites.
  La création réelle d’Agent utilise `architecture plan --file`, puis apply
  du plan autorisé. Les rails publics existants restent les autorités.
- Profil MCP natif optionnel `client-mcp-stdio` : 10 outils en lecture seule,
  21 avec les deux opt-ins locaux. Il fige config, contexte, workspace et
  chemins du One ; les appels utilisent des argv fixes sans shell RPC.
  Aucun outil d’approbation. Le runtime conserve exactement ses 3 outils,
  et D1 ses 5 outils. L’exécution front door reste sur son grant distinct.
- Refus avant effet des chemins traversants, symlinks, champs inconnus,
  mauvais types, objet invalide et changement de cible. Scaffold Application
  créé exclusivement, sans écrasement même en concurrence.
- Après révocation d’un grant de test : CLI `grant_invalid`, exit 4 ; même
  session MCP stdio déjà ouverte : `isError=true` et code `grant_invalid`.
  Claude CLI conserve lui aussi exit 4 et s’arrête. Le code repose sur
  l’erreur d’authentification typée/HTTP 401, jamais sur une recherche de texte.

## Preuves réelles

Claude Code CLI 2.1.306, modèle `claude-sonnet-5-5`, plugin 0.1.0 chargé
uniquement par `--plugin-dir`. Sessions sans persistance, mode restreint,
configuration MCP explicite, outils autorisés bornés ; aucun refus de permission
sur les cas nominaux. `control`, `builder-final`, `lifecycle-final`,
`runtime-final` et `revocation-final` ont un processus terminé avec succès.
Les résultats sont contrôlés indépendamment des conclusions du modèle.

Le build utilise un même plan persisté, une même clé et le même test réel
PASSED 1/1 : apply/test rejoués retournent `replayed=true`, puis verify CLI/MCP
retourne `verified=true`, sans dérive. Les identifiants et hashes exacts sont
consignés dans le [rapport structuré](AGENT-1034-native-interfaces.json).
Le lifecycle arrête puis redémarre seulement ce One, et vérifie son `/ready`.
Module et Application ont les mêmes fichiers produits par CLI et MCP ; le
pull initial des Specs créées par architecture est vérifié par les deux rails.

Le Workflow publié `native-list-proof@1.1` lit le storage fictif local :
`completed`, `{listed:true}`, un appel outil, aucun appel LLM. CLI `swarm run`,
MCP et une nouvelle conversation Claude CLI/MCP retrouvent le même Job et la
même exécution. Après tous ces rejeux, `used_effects=1`. Le coût zéro est une
qualification de test épinglée à cet outil, Agent, organisation et Spec hash.

Les lectures publiques Jobs demandent un principal Hanko ou une clé
Application admise. Le grant local front door ne reçoit pas ces droits :
la lecture croisée est un 404 opaque, pas une raison d’élargir les accès.
Un Job distinct créé via Hanko permet de vérifier list/get/events/logs,
limite 1, page suivante sans doublon, curseurs JSON et base64url.
Les contenus CLI/MCP sont identiques hors révision de snapshot actualisée par
le serveur entre deux lectures ; les deux révisions brutes sont conservées.
Lors de cette comparaison, ce Job est `blocked/validation_failed` : son contrat public historique exige
`{ok:true}` tandis que le Workflow renvoie `{listed:true}`. Sa lecture est
qualifiée ; son exécution n’est pas présentée comme un succès. Le parcours
front door réussi utilise le schéma de sortie publié du Workflow.
Après son délai de cinq minutes, le même Job passe à `expired`, en conservant
`blocked_reason=validation_failed`. Le premier reçu final a échoué car son
attente exigeait encore `blocked` ; cette attente est corrigée sans créer
un autre Job, et le reçu est rejoué sur ce même identifiant.

## Vérifications et limites conservées

Tests Go ciblés et suite courte CLI/API/frontdoor/controllers réussis ; le
changement final d’indépendance de `swarm run` vis-à-vis de la configuration
partagée a ses tests ciblés et sa preuve live avec un chemin config absent,
qui n’est jamais créé. Les 21 selftests du dépôt (dont 4 de packaging) passent et `claude plugin
validate` réussit. Le Skill canonique 2.0.39 et son bundle sont inchangés.
L’archive qualifiée a le SHA-256
`6d112a1797faf80a0084ad0217937a9910de9daf59ee4214a251cc60068536ba`.

Les échecs du harnais restent distincts des preuves vertes : flag lifecycle
`--wait` corrigé en `--timeout`, argument vide `list_files` corrigé par plan
Spec puis nouvelle version publique relue, et lock généré committé avant pull.
`code_execution` n’est pas admissible par le front door de cette campagne.
Les décisions fictives d’approbation déjà qualifiées sont conservées dans
[la campagne précédente](AGENT-1034-parity-approval.md), sans nouvelle
revendication de clic humain physiquement distinct.

`nodes` projette les accès du principal, sans inventaire fleet générique.
Le profil local utilise le credential CLI explicitement choisi ; il ne
transforme pas un grant distant en accès opérateur et n’est pas une sandbox OS.
Un SDK MCP HTTP tiers neuf peut afficher sa propre erreur d’authentification ;
le statut HTTP reste 401, sans distinguer publiquement expiration et révocation.
La qualification Codex AGENT-613 reste historique ; ce rapport n’annonce pas
une nouvelle qualification Codex, Claude Desktop, marketplace ou production.

La gate `work:start` a réussi avec la dérogation WIP ciblée déjà autorisée,
autres contrôles conservés. Le reçu One commun est produit **après le commit de
ce rapport**, aux deux HEAD finaux, et rapporté dans PR54 avec l’état de la
soumission backend GitLab. Cette note ne vaut ni fusion, ni release, ni closeout.

Carte de code utilisée :
`ripwire . --query='CLI MCP local adapter root command job list application jobs node inventory context network allowlist' --top-k=10 --max-tokens=3200`.
Contrôle borné complémentaire :
`ripwire apps/mauricecli --for='client-control swarm build lifecycle jobs nodes front door'`.
