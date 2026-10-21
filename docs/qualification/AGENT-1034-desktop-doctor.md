# Claude Desktop Doctor — AGENT-1034

**Statut du parcours borné : passed.** Ce rapport documente la campagne Claude
Desktop du 21 octobre 2026 sur le One `agent-1034-interfaces`. Trois tours dans
une nouvelle session dédiée, avec `enabledMcpjsonServers` local configuré pour
`maurice_local` et `maurice_runtime`, valident la continuité et le replay
idempotent sur cette cible. L'incident de la session précédente reste conservé
comme preuve négative historique. Cela ne prouve pas une cause générale ni une
qualification sur des versions supérieures. La PR plugin est Draft, Plane est
In Progress et aucun closeout, merge ou release n'est revendiqué.

## Cible et versions

- backend qualifié : `2f3af26ca91438bfb27d034b6358ff6252a0a189` ;
- One : `agent-1034-interfaces`, API `127.0.0.1:43700`, front door
  `127.0.0.1:43731` ;
- Desktop `3.1623.0` (macOS `27.0.1`, arm64), CLI embarquée `2.1.304`, CLI
  `2.1.306` ;
- session Desktop/CLI de l'incident historique :
  `764a2f90-f2a9-423c-b347-0bc1e221af2a` ;
- session Desktop/CLI de la preuve finale : UI
  `local_b5a18e50-7bf8-46ff-8c12-36eeeec9e19b`, CLI
  `bc1876c8-aa59-4e55-988a-2137b0596a56` ; aucune autre session utilisateur
  n'a été utilisée.

Les preuves d'archive et de transcript sont respectivement
`f8210dabe58c07c07811851ae8cef69ce9eb4f9fa73e2455b96ebe4856d0737b` et
`b2f8b13412bb5a21d0f77625525ba9579458727da1d26646b460e1d97b772fa3`.

## Tour 1 : preuve MCP et Workflow

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

## Continuité finale : dix assertions sur trois tours

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

## CLI Desktop : cinq assertions indépendantes

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

## Doctor : ce qui est et n'est pas prouvé

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

La campagne rapporte 22 selftests Python, dont 5 contrôles de packaging. Une
suite courte Go séparée a duré `47.075 s`. Le parcours CLI indépendant a validé
7 assertions via `assert_cli_final.py`; la preuve de continuité ci-dessus ajoute
10 assertions sur trois tours.

Conclusion actuelle : le parcours Desktop borné, avec la nouvelle configuration
locale et la nouvelle session, est **passed** pour cette cible et cette archive,
y compris la continuité et le replay idempotent. L'incident de la session
historique reste non résolu quant à sa cause générale. Le statut de livraison
demeure PR Draft / Plane In Progress, sans closeout ; le viewer, la readiness VM
publique et le chat LLM restent hors preuve Doctor.

La carte de code a été consultée avec :

```text
ripwire . --for='AGENT-1034 work submit backend merge request GitHub pull request closeout Plane multi-repo purge One sandbox active interfaces' --signatures-only --pack-top-n=20
```

Sources publiques de campagne : `artifacts/desktop-final-mcp.json`,
`artifacts/desktop-final-cli.json`,
`artifacts/desktop-final-continuity.json`,
`artifacts/desktop-second-turn-blocked.json`,
`artifacts/doctor-final-parity.json`, `artifacts/client-versions-final.json`
et `public-scope.json` sous `/private/tmp/agent1034-interfaces`.
