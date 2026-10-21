# Parité CLI/MCP et approbations Claude — AGENT-1034

> **Statut documentaire — campagne historique supersédée.** Ce document décrit la campagne menée sur l’archive 2972c5fee9e2f947795f40ccaaf71399d61397d4646120fd9aad860f6d85ea6e et le backend 4fd020849d7fa52361d371bd5dfbfceb48991e3c. L’état natif actuel qui fait foi est la [qualification des interfaces natives](AGENT-1034-native-interfaces.md) et sa [preuve JSON](AGENT-1034-native-interfaces.json), avec l’archive c14728298a9ec8a46701bd19fbe1822e20a64c6faa74c234f09c61e815cb699e et le backend de qualification 0df11b39c716d710ed01fd405db2a4da90b0294f (backend final fb0b0d679d01dd81ce94fa9e8a984d2833d80971).

Campagne complémentaire du 21 octobre 2026 : **18 conversations réelles**
Claude Code **2.1.306**, modèle **claude-sonnet-5-5**, dans des processus
séparés lancés depuis notre shell. Aucune session Claude existante, aucun
réglage global, aucune stack partagée modifiés. Backend propre
`4fd020849d7fa52361d371bd5dfbfceb48991e3c` ; même archive Claude
`2972c5fee9e2f947795f40ccaaf71399d61397d4646120fd9aad860f6d85ea6e`.

Les **21 tests** de packaging/diagnostic et la validation native stricte Claude
ont été relancés avec succès. La Skill canonique et le paquet restent inchangés.

La [preuve structurée](AGENT-1034-parity-approval.json) conserve les entrées,
réponses, erreurs et digests des transcripts. Ses assertions indépendantes
comparent les objets retournés et les fichiers réellement transmis, puis
contrôlent les effets dans les seules bases de test en lecture seule.
Le champ JSON `independent_verification` identifie la commande réellement
exécutée par le parent, son horodatage, le digest de son source et l’extrait
qui contrôle les deux absences de fichier, les Jobs et les effets. Ces
contrôles sont distincts des transcripts Claude, qui disent à juste titre
ne pas avoir eux-mêmes lu ces fichiers.
Cette campagne complète les [commandes swarm/build](AGENT-1034-commands.md)
et la [première qualification Claude](AGENT-1034-claude.md).

## Décisions de test : délégation explicite

Le fondateur a explicitement autorisé l'agent à accepter et refuser les
cartes fictives de cette qualification. Le parent a donc utilisé l'interface
publique du One dans un **navigateur headless neuf lancé depuis son shell**,
avec une session créée par `maurice home`. Aucun cookie utilisateur existant,
credential forgé ou endpoint privé n'a été utilisé.

Le serveur voit le principal natif `local-operator`, distinct du grant de
l'assistant. L'acteur qui clique est toutefois **l'agent, sur délégation
explicite**, et non un humain physiquement séparé. Cela qualifie la mécanique
des cartes et de la reprise dans ce scénario de test ; cela ne constitue pas
une délégation générale des approbations produit ou de production. Les sessions
Claude pilotées n'ont reçu aucun outil permettant de résoudre les cartes.

## Résultats vérifiés

| Parcours | Preuve et résultat |
| --- | --- |
| Check CLI/MCP | Même requête, contenus des fichiers et provenance ; tous les champs serveur communs strictement identiques, y compris spec_hash, diagnostics, cible, version de base, policy et bundle. Les champs locaux ajoutés par la CLI sont distingués. |
| Plans CLI et MCP | Même source, spec_hash, base version, diff, fingerprints et politiques. Enveloppes indépendantes : plan_id et plan_hash différents. On ne présente pas deux créations de plans comme le même artefact. |
| Apply partagé | Plan `dbcdmj24p5cmlnj4usv0`, hash `b45c5e2ca2509d1324d453605112dd4c85ea06e6dffc512ec0f2e41a38981f3e`. Apply CLI nominal puis même plan/autorisation/clé en MCP : replayed=false puis true, mêmes apply/evidence/applied_at, version 6. |
| Tests et verify partagés | Test run unique `dbcdpai4p5cmlnj4v210`, statut PASSED, 1/1. Verify CLI et MCP : objets JSON égaux, verified=true, drift=false, même rapport et mêmes empreintes. |
| Carte initiale CLI/MCP | Lectures du même pending_action : objets strictement identiques, waiting avant décision, aucune exécution. |
| Accord puis seconde gate | Carte initiale `ha_dbcdio24p5cmlnj4us10` acceptée par le parent délégué ; nouvelle session Claude observe approved et reprend la même demande. Elle obtient la carte d'étape `ha_dbcdnf24p5cmlnj4utjg` et s'arrête avant l'écriture. |
| Accord d'étape et résultat | Après accord délégué de l'étape write, reprise MCP puis CLI : objets d'exécution égaux, Job `dbcdnf24p5cmlnj4ut1g`, exécution `e9fvr96fk8ejgiqipg1g`, completed, résultat déclaré et readback corrects. |
| Redémarrage et nouvelle conversation | Arrêt/démarrage publics du seul One A, puis nouveau processus Claude : mêmes ref, entrée, clé et hash attendu ; mêmes Job/exécution/résultat par MCP et CLI, aucun nouvel effet. |
| Refus | Carte `ha_dbcdkai4p5cmlnj4us3g` refusée par le parent délégué. Nouvelle session Claude observe decision=rejected, status=completed et ne rappelle pas execute. Le fichier refusé reste absent. |
| Révocation dans une session déjà connectée | Search/explain réussis, révocation explicite du grant temporaire, puis execute MCP refusé avec authorization required ; CLI refusée avec frontdoor_call_failed, exit 1. Aucun autre grant, retry ou fallback créé par Claude. Le fichier reste absent et aucun nouveau Job n'existe. |
| Changement A → B | Une même conversation vérifie A, bascule sur B, relit le scaffold de B et ne rappelle plus le profil A. Un plan de A est NOT_FOUND dans B ; la CLI avec le contexte B refuse context_workspace_mismatch avant apply. Un complément compare le même identifiant de plan des deux côtés. Le code CLI plan_target_mismatch n’est pas revendiqué : le contrôle du contexte bloque plus tôt. |
| Incompatibilité à la connexion | Profil MCP au bundle volontairement faux : HTTP 426, connexion failed, aucun outil métier chargé, aucune réparation ou connexion alternative. |
| Incompatibilité avant apply | Une session correctement connectée envoie volontairement client_contract v1 et un bundle faux : client_contract_incompatible avant mutation. Aucun retry corrigé dans ce cas. |

Aucun champ `plan_hash` n'est inventé dans les réponses front door d'exécution,
qui ne le renvoient pas ici : la conservation du hash est vérifiée sur les
entrées execute/CLI et les cartes. Les réponses d'exécution sont comparées
sur leurs champs effectivement présents.

## Preuve indépendante des effets

Le One A conserve exactement les trois Jobs historiques et **un seul nouveau
Job**, celui du parcours avec approbation. Pour ce dernier, le journal
contient exactement une entrée confirmée pour `__workflow_launch`, une pour
`write` et une pour `read`, y compris après redémarrage et replays.

Le seul fichier nouveau attendu contient `Accord humain Claude AGENT-1034`,
SHA256 `6739c5695bed76f348417e9f86a75b7ba872e7a81b76eeb33a7eb30a5216a449`.
Les fichiers des cas refusé et révoqué sont absents. Le fichier commun de la
première campagne garde son hash initial. Le One B ne contient aucun AgentJob.
Le Job D1 historiquement bloqué est maintenant expiré ; son échec initial
reste conservé dans les preuves précédentes.

## Échecs conservés et limites

- Le premier replay d'un ancien plan a été refusé `git_workspace_dirty` :
  seul le lock généré restait non commité. Après revue et commit de ce lock,
  le même ancien plan a été refusé `plan_source_changed`. Aucun flag de
  contournement, reset ou réécriture de provenance n'a été utilisé. Le cas
  nominal utilise un nouveau plan autorisé par policy, puis partage ce plan
  exact entre CLI et MCP.
- Le premier appel MCP plan a mal retranscrit un fichier. Le serveur a refusé
  le workspace_hash incohérent avant création du plan. La tentative corrigée
  transmet ensuite les contenus exacts, vérifiés octet pour octet par le
  collecteur. L'erreur reste dans la preuve et n'est pas comptée comme un
  premier essai réussi.
- Le premier pull sur B a omis instance_url ; INVALID_CONFIG est conservé.
  Il a été refait uniquement avec l'origine B explicitement donnée. Aucun
  résultat de A n'a été réutilisé comme résultat de B.
- Le One B officiel avait son kill switch External Inception désactivé.
  Le bootstrap a d'abord été refusé ; la capacité a été activée uniquement
  dans son processus de test par les commandes publiques de lifecycle.
  Le seed et les binaires officiels sont conservés. Cela ne prouve pas que
  tous les profils One exposent MCP par défaut.
- La révocation bloque bien les effets, mais la **parité des diagnostics
  reste incomplète** : le client MCP voit authorization required et la CLI
  ne restitue ici que frontdoor_call_failed. On ne revendique pas le code
  structuré grant_invalid dans ces sorties.
- Les décisions d'approbation sont des tests délégués, pas des clics humains
  physiquement distincts. Claude Desktop Code n'est pas qualifié ; seule la
  surface CLI est annoncée ici, conformément à la demande du fondateur.

Les grants temporaires de cette campagne sont révoqués. Les deux derniers
préflights authentifiés échouent comme attendu et ne créent aucun fichier de
configuration ; la preuve de nettoyage est incluse dans le JSON.

## État du lot

Les parcours disponibles ci-dessus sont qualifiés dans leurs limites.
**PLUG-12 universel reste non satisfait** : inventaire fleet générique,
lifecycle/scaffold local sans équivalent MCP distant, et différence entre
D1 single-job et CLI job graph/list. Une qualification ne peut pas créer ces
interfaces manquantes. Le rapprochement sémantique des plans ne remplace pas
le partage d'un même plan persisté pour la parité apply.

AGENT-1034 reste **In Progress**, PR **Draft**. Mod/dev, publication distante,
marketplace et production ne sont pas couverts. Les preuves et le reçu
standard du SHA de cette campagne historique sont rapportés dans la PR ; aucun work:submit ou
closeout réussi n'est revendiqué.
