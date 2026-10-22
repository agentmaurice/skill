# Qualification du plugin Codex Desktop — AGENT-613

Qualification locale du 22 octobre 2026 sur données fictives, encore en cours.
Le plugin est installé et chargé dans le client réel ; les parcours direct,
idempotent, approuvé et révoqué sont vérifiés. Le refus d’une carte reste à
qualifier dans un second chat, dont la création attend une autorisation.
La preuve CLI historique demeure dans [son rapport](AGENT-613-codex.md).

## Client, paquet et environnement

- Client réel : ChatGPT Desktop 26.1013.40934, build 20770, bundle
  `com.openai.codex` ; CLI embarqué `0.163.0-alpha.10.2`.
- Modèle `gpt-6.1-sol`, raisonnement `high`, vérifié dans les seuls
  `turn_context` du chat de qualification.
- Projet local dédié `maurice-plugin`, dossier
  `/private/tmp/agent613-desktop/project`. Chat principal :
  `01a161d4-7806-78d0-ae56-f83c773dd832`.
- Plugin privé `maurice 0.1.0`, Skill canonique `2.0.40`, source
  `64c980c6ce787c4e19bfbc7522998f9e2b4d1584`.
- Archive SHA-256
  `883c1d675cdb509143e2827e9789ae5525be139c7f27200299a017c0694f11ab`.
  Contenu canonique
  `dbcd1b40538d1fab245c76849e4b3a7c371f4b15ff954ef8d60afb34950ad50b` ;
  bundle
  `781642b0dd961739c8051c117259544e0f410b4cdd70f7555d3551c956c2d0c9`.
- One natif isolé `agent-613-desktop`, backend figé au commit
  `df523801ccef28cd03eb8ce4f94ca4030854d72f`. Aucun OS démarré.
  Le provider BYOK de test existe, mais les deux Workflows de stockage
  synthétiques n’utilisent aucun appel LLM AgentMaurice.
- Deux mandats consommés, chacun limité à un seul Workflow et un seul run,
  ont été révoqués. Le troisième, pour le refus, est limité au même Workflow,
  un run et une heure ; émis le 22 octobre 2026, il expire à 05:38:59 UTC.
  Son état actif décrit ici est celui de la préparation du cas.
  Aucun jeton n’est inclus dans les preuves publiques.

## Résultats réellement observés

| Parcours | Observation dans Desktop et contrôle serveur |
| --- | --- |
| Accueil | Le chat voit d’abord les six outils MCP, mais signale correctement le Skill absent. Aucun effet métier pendant cet accueil. |
| Installation | Le CLI officiel installe le plugin. L’activation utilisateur est immédiatement passée à `false`, celle du projet reste `true`. Les autres réglages sont conservés. Tous les fichiers installés sont identiques à la source. |
| Chargement | Au tour suivant, le catalogue fourni par le client expose réellement `maurice:use-maurice`, puis le modèle lit les instructions installées. Un contexte témoin dans un projet isolé ne charge pas ce Skill. Aucun redémarrage de Desktop. |
| Direct | Avant chargement du Skill, le parcours MCP écrit puis relit `/qualification/codex-desktop-real.txt`, avec `recorded=true`. Job `dbcp42a4p5cp07nm5ac0`, exécution `449i4c0mmbmuk3mco0k0`. Ce premier parcours qualifie le MCP. |
| Rejeu avec Skill chargé | `search`, `explain`, puis `execute` avec mêmes référence, entrée, hash et clé. Le résultat retrouve le même Job et la même exécution. SQLite, quota et hash du fichier confirment un seul run et aucun doublon. Ce rejeu n’est pas un test de redémarrage. |
| Accord distinct | Attente avant démarrage, carte `ha_dbcp55i4p5cp07nm5c10`, puis avant écriture, carte `ha_dbcp6aq4p5cp07nm5cng`. Le plugin explique chaque carte et s’arrête. Après les décisions du pilote, il reprend avec la même clé et distingue le résultat métier du statut de carte. |
| Résultat approuvé | Job `dbcp6aq4p5cp07nm5c5g`, exécution `0okkje2c2ovmankg7m50`, statut `completed`, fichier `/qualification/codex-desktop-approved.txt` écrit puis relu avec le message attendu et `recorded=true`. Deux Jobs completed au total. |
| Révocation | Après révocation par le propriétaire, les lectures natives direct et approval renvoient `isError=true`, `structuredContent.error.code=grant_invalid`. Le modèle arrête le parcours sans execute, nouvelle clé ou rebranchement. La CLI renvoie aussi exit 4 ; Jobs et fichiers restent identiques. |
| Refus de carte | Encore en attente. Le nouveau serveur MCP du mandat de refus n’apparaît pas dans le chat existant ; le modèle s’arrête sans appel métier. Une seconde création de chat est demandée avant de poursuivre. |

Les décisions des deux cartes ont été réalisées dans la véritable interface One
par le pilote de qualification, selon l’autorisation explicite du fondateur
pour les tests fictifs. Elles ne sont jamais soumises par le plugin. Ce test
ne prouve pas une présence humaine ; il qualifie l’attente et la reprise du
client face à des décisions réellement enregistrées par le serveur.

Les Workflows synthétiques écrivent sans écrasement puis relisent une cible
sous `/qualification/codex-desktop-*.txt`. Deux fichiers de seed relèvent
uniquement des tests de la Spec. Au dernier contrôle, deux Jobs completed et
les deux fichiers métier attendus sont présents ; le fichier refusé est absent.

## Installation et limites du client

Le dossier doit être ajouté comme projet local. Le joindre à un prompt a
produit un premier essai négatif dans un chat projectless : lecture des sources,
aucun MCP disponible, arrêt sans effet. Cela n’est pas une installation active.

Un catalogue source, un réglage `enabled=true` et un cache installé sont trois
états distincts. L’installation officielle a été répétée dans un `CODEX_HOME`
isolé avant d’utiliser le CLI embarqué du vrai Desktop. Son `plugin add`
active le plugin au niveau utilisateur ; cette entrée a été immédiatement
désactivée et l’activation projet conservée. La configuration finale est
vérifiée dans le projet et dans un projet témoin. Le cache n’est pas édité
manuellement. Voir [l’installation](../install.md#projet-dédié-dans-codex-desktop).

Le Skill ajouté apparaît dans le même chat au tour suivant, mais un nouveau
serveur MCP ajouté au projet n’y apparaît pas. Les connexions doivent donc
être préparées avant de créer le chat. Le mandat approval ayant consommé son
quota, le cas de refus utilise un troisième mandat avec quota disponible ;
aucune augmentation du budget consommé ni nouvelle clé ne contourne le garde.

Cette campagne ne qualifie ni publication marketplace, ni ChatGPT distant,
ni disponibilité d’un binaire AgentMaurice publié, ni redémarrage de Desktop,
ni qualification générale du Viewer. Claude et ses sessions ne sont pas utilisés.

## Preuves et contrôles

[La transcription native réduite](AGENT-613-codex-desktop-native.json) contient
la provenance du client, la présence du Skill dans son contexte et les appels
MCP structurés. Elle exclut reasoning, instructions système, catalogue tiers,
configuration, credentials et autres sessions. Les contrôles du serveur sont
conservés séparément : ils corroborent Jobs, quotas et fichiers, mais ne prouvent
pas à eux seuls une provenance Desktop.

Les deux validateurs de Skills et les 22 selftests Python de la CI réussissent
localement. Le paquet a également été comparé : 35 fichiers canoniques sans
divergence, 39 entrées d’archive et cinq tests packaging réussis.

Exploration : `ripwire . --query='Codex plugin marketplace AGENT-613 qualification'
--top-k=5 --max-tokens=1500`, puis lectures ciblées ; pour le contrat quota,
`ripwire <checkout-backend> --for='explain workflow effect_quota quota'`.

## Gouvernance et état de livraison

AGENT-613 reste In Progress. Une admission `work:start` a réussi avant toute
restauration. Un premier échec HTTP 429 a été repris en respectant le délai
GitLab, avec les mêmes credentials et tous les contrôles canoniques.

Une clôture prématurée a été constatée à 05:51:58, avec purge du One et du
worktree déjà fusionné. Les anciennes sections de clôture CLI étaient encore
validantes malgré le complément Desktop incomplet. Elles ont été renommées
historiques ; le validateur refuse désormais la clôture. La fiche a été rouverte
et les ressources restaurées après la nouvelle admission. L’acteur déclencheur
n’est pas établi. Les preuves avant cet incident ne sont pas présentées comme
celles du One restauré.

Le contrôle Cua interdit le pilotage de Codex Desktop. La création et les tests
dans le seul chat dédié passent par les outils natifs de l’application,
explicitement autorisés par le fondateur. Aucun autre chat n’est lu ou piloté.
La seconde création demandée, le refus, la revue finale, la CI distante et la
clôture restent en cours. Aucune réussite complète n’est annoncée à ce stade.
