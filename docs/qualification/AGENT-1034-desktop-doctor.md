# Claude Desktop Doctor — AGENT-1034

**Statut de la soumission Desktop bornée : passed.** Le parcours Claude Desktop
complet est maintenant prouvé sur le One `agent-1034-interfaces` avec le backend
`df523801ccef28cd03eb8ce4f94ca4030854d72f`, l'archive
`54e72b58181a78f089242407e0b7870bcf8b72a078424be6efd9339de4dfa27c` et le
Skill `2.0.40`. La vérification finale ajoute huit assertions au quatrième échange, avec le
nouveau plan et son test `PASSED 1/1`. Les preuves post-main
précédentes sur `68454b62` restent séparées ; la campagne ne revendique pas de
cause générale au-delà de cette session.
À l’enregistrement de cette qualification, la PR plugin est Draft et Plane
est In Progress. La soumission, la CI, les merges et le closeout sont suivis
séparément dans les PR et le ticket.

## Cible et versions

- backend qualifié pour la soumission Desktop : `df523801ccef28cd03eb8ce4f94ca4030854d72f` ;
- One : `agent-1034-interfaces`, API `127.0.0.1:43700`, front door
  `127.0.0.1:43731` ;
- Desktop `3.1623.0` (macOS `27.0.1`, arm64), CLI embarquée `2.1.304`, CLI
  `2.1.306` ;
- session Desktop/CLI post-main : UI
  `local_53e0a462-f887-4278-b667-c3ed5d06e7f7`, CLI
  `74f4b1f5-14ec-444c-a5cf-8a317ff3e584` ;
- preuves historiques conservées : backend
  `2f3af26ca91438bfb27d034b6358ff6252a0a189`, archive
  `f8210dabe58c07c07811851ae8cef69ce9eb4f9fa73e2455b96ebe4856d0737b`.

Le transcript de la continuité post-main porte le SHA-256
`947a1c8a0f156ab8473770d859173a49f96f6de7723c85f655107915eb25280b`.

## Campagne post-main précédente — backend 684

`desktop-main-merged-continuity.json` est `passed` avec 13 assertions sur trois
tours : accueil sans effet, même contexte, même statut/PID, même Doctor, quota
`0 → 1 → 1`, aucun Job supplémentaire, cinq commandes littérales, égalité CLI /
MCP pour `status`, `check` et `verify`, quatre réponses runtime identiques,
égalité binaire du plugin installé et absence d'édition ou de reconnexion.
Le Job runtime est `dbchflq4p5cv5v09a07g` et l'exécution
`af0sp80p5ivmdgvuj41g`.

Les artefacts dédiés confirment en outre huit assertions MCP dans
`desktop-main-merged-mcp.json` (transcript
`4ba961821477d4f32d9a290774b6e4463773c2bb044a61b0050936efcedae328`) et cinq
assertions CLI dans `desktop-main-merged-cli.json` (transcript
`08152c0a21c7f24d72480ea4236d95c3d770e6387e5614b1434394f1c68810c8`). Les
cinq parcours `main-merged` sont `PASS` et `assert_cli_main_merged.py` rapporte
sept assertions réussies. Le package source et le plugin installé sont
identiques octet par octet dans `desktop-main-merged-plugin-byte-equality.json`.

La configuration et les sessions post-main ont résolu le parcours observé sur
`68454b62` ;
elles ne constituent pas une cause générale de l'incident historique. Le
backend `df523801ccef28cd03eb8ce4f94ca4030854d72f` contient seulement les
un ajustement de quatre lignes dans `internal/wasmexec/runner_test.go` après
`68454b62`. Cette durée et ces contrôles Go appartiennent à `68454b62`, pas à la
preuve Desktop finale `df` ci-dessous.

Le Skill post-main est `2.0.40`, content hash
`dbcd1b40538d1fab245c76849e4b3a7c371f4b15ff954ef8d60afb34950ad50b` et bundle
`781642b0dd961739c8051c117259544e0f410b4cdd70f7555d3551c956c2d0c9`.

## Soumission finale Desktop — backend df

`desktop-final-submission.json` est `passed` sur la même UI
`local_53e0a462-f887-4278-b667-c3ed5d06e7f7` et le même CLI
`74f4b1f5-14ec-444c-a5cf-8a317ff3e584`. Ses huit assertions sont vraies :
contexte lié, One running, health/MCP Doctor, verify sans dérive, quatre
empreintes (`artifact`, `plan`, `expected`, `observed`) dont le `backend_commit` est `df`, deux replays
exacts retrouvant le même Job `dbchflq4p5cv5v09a07g` et la même exécution
`af0sp80p5ivmdgvuj41g`, quota à un et absence de shell, édition ou
reconnexion.

Le plan exact est `dbchipa4p5cgi1pqha10`, de hash
`aa49af15cc9d753aeaae92a922f8237286362633c5b34d9276dfdb263aa938d1`, et le
test reçu `dbchipa4p5cgi1pqha40` est `PASSED` `1/1`. Les deux `execute` ont la
même clé `native-1034-main-merged`; `explain` avant et après conserve le quota
à un. Le transcript de cette soumission porte le SHA-256
`2804c2966ed8fe454b8dca5d96b397f8f83fe4b2e1f99b2a688da72da2178df7`.

Cette preuve qualifie le parcours Desktop borné sur `df` et l'archive `54e72b…`.
Elle ne réattribue pas la suite Go `41.368 s`, qui reste une preuve de la phase
`68454b62`, et ne transforme pas la revue backend en qualification plus large.

Les [extraits de réponses natives et leurs empreintes](AGENT-1034-client-evidence.json)
conservent les appels et résultats pertinents. Le [reçu adverse Doctor](AGENT-1034-doctor-adverse-review.json)
garde les six constats et la réfutation du seul bloquant de nomenclature ; le
validateur officiel accepte le HEAD `df523801` sans exemption.

## Preuves historiques conservées — backend 2f / archive f821

Les sections suivantes conservent les preuves de la campagne précédente ; elles
ne remplacent pas la campagne post-main ci-dessus.

## Tour 1 historique : preuve MCP et Workflow

`desktop-final-mcp.json` est `passed` et ses huit assertions sont vraies :
contexte, statut, build check, build verify, Doctor, même résultat de replay,
quota d'effets `0 → 1` et absence de shell. Dans cette session, les appels
MCP locaux ont confirmé le contexte et l'état du One, puis `check`, `verify` et
`doctor`. Le parcours runtime a été :

1. recherche puis explication de
   `workflow:dbcehma4p5cvd8sl2bug/native-list-proof@1.1` ;
2. deux appels `maurice_execute` avec la même entrée, la même clé
   `native-1034-final-reviewed` et le même hash de plan ;
3. résultat identique : Job `dbch3d24p5cpua8dvmk0`, exécution
   `eheq4jq9ul6mr1ghb100`, `status=completed`, `{"listed":true}` ;
4. `explain` final : un effet consommé, zéro effet restant et zéro appel LLM
   dans l'exécution.

Le plan appliqué est `dbch1fi4p5cpir4sqsk0`, de hash
`37082f639cf413b52ecc05d57a5a35da668e63554021866e78cfdfb63b2b2c81`, et le
hash de Spec qualifiée est
`36eb72546e747206bb485f719401a3dda10579f3455aa227917f44a2a4493528`.
Cette preuve porte sur ce Workflow local et ne vaut pas qualification générale
du plugin ni du chat LLM.

## Continuité historique : dix assertions sur trois tours

`desktop-final-continuity.json`, produit par `assert_desktop_continuity.py`, est
`passed` avec dix assertions sur trois tours dans la nouvelle session : même
contexte, même statut et PID, même Doctor, `check` égal, `verify` égal, deux
replays exacts, même Job/exécution/résultat, quota restant à un, aucune nouvelle
exécution et absence de shell ou de reconnexion. Les deux replays utilisent la
même clé `native-1034-final-reviewed` et retrouvent le Job
`dbch3d24p5cpua8dvmk0` et l'exécution `eheq4jq9ul6mr1ghb100` ; l'historique ne
contient pas de nouveau Job.

Le projet Desktop a ajouté uniquement, dans ses réglages locaux non suivis,
`enabledMcpjsonServers=[maurice_local,maurice_runtime]`. Aucune permission
Bash ni configuration globale n'a été changée. Cette configuration et cette
session résolvent le parcours observé ; elles n'établissent pas la cause
générale de la rétraction de la session historique.

## CLI Desktop historique : cinq assertions indépendantes

`desktop-final-cli.json`, produit par `assert_desktop_cli_final.py`, est
`passed`. Les cinq assertions indépendantes sont vraies : les cinq commandes
correspondent exactement à `public-commands.json`, puis les résultats JSON de
`status`, `check`, `verify` et des deux exécutions sont égaux à ceux du tour 1
MCP. Le Job, l'exécution et le résultat sont donc les mêmes sur ce parcours
CLI. Son transcript porte le SHA-256
`300afaa03cfb9921631f1d9a9c753e071c3a4a6e81fa2221ab6debf2d60406d3`.

Cette preuve CLI complète le tour 1 ; elle ne rétablit pas la continuité MCP
du tour 2 et ne change pas le refus initial de la commande composée avec
`echo`, qui est restée non exécutée sans changement de permission Bash.

## Doctor historique : ce qui est et n'est pas prouvé

La CLI et `maurice_doctor` sont égaux (`cli_exit=0`, `equal=true`) dans
`doctor-final-parity.json`, avec 22 outils dans le profil. Le health check, le
storage check et la reachability du catalogue front door sont positifs.

Doctor signale toutefois :

- `one_home.missing_viewer_dist` en blocage : aucun bundle viewer utilisable
  avec `index.html`, donc la page One ne peut pas être déclarée ouvrable ;
- `home_profile` non enregistré et `vm_profile_readiness.checked=false` : la
  readiness d'une VM publique n'est pas vérifiée ;
- `llm_actor_checked=false` et `llm_actor_live=false` : aucun contexte
  AgentMaurice n'est lié, donc le parcours chat LLM n'est pas vérifié.

Le Doctor prouve le handshake et le catalogue accessibles, pas l'ouverture du
viewer, une VM publique, un grant métier ou un chat LLM.

## Incident historique du tour 2 : continuité non qualifiée

`desktop-second-turn-blocked.json` porte le statut `blocked_on_second_turn` pour
la session historique seulement.
Au tour suivant, les 14 outils `maurice_local`/`maurice_runtime` ont été
retirés avec la cause `not_configured`; aucune nouvelle connexion MCP n'a été
établie et aucune exécution CLI de remplacement n'a eu lieu. Le root cause de
la rétraction n'est pas prouvé. La preuve on-disk de configuration ne permet
pas, à elle seule, de conclure que le problème vient du plugin, de Desktop ou
du harness.

Le fallback Bash a également été refusé avant exécution : la commande autorisée
a été suffixée par `; echo "EXIT=$?"`, puis le classifieur Claude Code a
retourné `[Auto-Mode Bypass]`. Les commandes suivantes n'ont donc pas été
exécutées et aucun code de sortie ne peut être rapporté pour ce fallback.

Les essais historiques du harness ont comporté un plan ancien et un dossier
parent hors cible ; ils sont conservés comme limites de harness, pas comme
échecs du backend final. Le contrôle négatif Doctor a par ailleurs refusé
`data_dir` avec `client_arguments_invalid: unknown field data_dir`; ce refus est
attendu pour l'injection négative et n'est pas un succès fonctionnel.

## Contrôles complémentaires et décision

La campagne post-main rapporte 22 selftests Python, dont 5 contrôles de
packaging. Une suite courte Go séparée a duré `41.368 s`. Les cinq cases
`main-merged` sont `PASS` et `assert_cli_main_merged.py` rapporte 7 assertions
réussies. Les chiffres `47.075 s` et `assert_cli_final.py` appartiennent à la
campagne historique f821 et restent conservés dans ses preuves.

Conclusion actuelle : le parcours Desktop borné est **passed** pour le backend
`df523801` et l'archive post-main, y compris la continuité et le replay
idempotent. Les preuves `684/f821` restent historiques ou préalables selon
l'archive. Le statut de livraison demeure PR Draft / Plane In Progress, sans
closeout ; le viewer, la readiness VM publique et le chat LLM restent hors
preuve Doctor.

La carte de code a été consultée avec :

```text
ripwire . --for='AGENT-1034 work submit backend merge request GitHub pull request closeout Plane multi-repo purge One sandbox active interfaces' --signatures-only --pack-top-n=20
```

Sources publiques de campagne : `artifacts/desktop-main-merged-mcp.json`,
`artifacts/desktop-main-merged-cli.json`,
`artifacts/desktop-main-merged-continuity.json`,
`artifacts/desktop-main-merged-plugin-byte-equality.json`,
`artifacts/desktop-final-submission.json`,
`artifacts/main-merged-cli-build-apply-replay.json`,
`artifacts/main-merged-cli-build-verify.json`,
`artifacts/doctor-main-merged-parity.json`,
`artifacts/backend-doctor-main-merged-review.json`,
`docs/qualification/AGENT-1034-doctor-adverse-review.json`,
`artifacts/desktop-second-turn-blocked.json`,
`artifacts/doctor-final-parity.json`, `artifacts/client-versions-final.json`
et `public-scope.json` sous `/private/tmp/agent1034-interfaces`. Les journaux
de contrôles sont `/private/tmp/agent1034-interfaces/merged-main-plugin-tests.log`
et `/private/tmp/agent1034-interfaces/merged-main-cli-full-short.log`.
