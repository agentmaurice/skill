# Build AgentMaurice depuis Claude

Cette référence décrit le raccourci conversationnel `maurice build` pour les
interfaces CLI AgentMaurice V2 exposées dans le backend de qualification
AGENT-1034. La qualification dépend du binaire et de l’instance utilisés ; consulter les preuves AGENT-1034. La release générale reste distincte.
Un build est un parcours ciblé qui doit toujours nommer
l'organisation, l'Agent ou l'Application, l'environnement, le répertoire de
projet et la source de connexion.

Les liens suivants sont relatifs à l'arborescence du paquet installé :

- [Agent Spec V2](../../agentmaurice/references/agent-spec-v2.md) pour la
  structure, les contrats et la politique d'environnement ;
- [Application delivery](../../agentmaurice/references/app-delivery.md) pour
  la livraison et la consommation d'une Application ;
- [Modules](../../agentmaurice/references/modules.md) pour le cycle d'un
  Module ;
- [Expert operations](../../agentmaurice/references/expert-operations.md)
  pour le diagnostic, le sandbox et les erreurs de gouvernance ;
- [Maurice front door](../../agentmaurice/references/frontdoor.md) pour la
  surface MCP de consommation `maurice.search`, `maurice.explain` et
  `maurice.execute`.

## Préflight obligatoire

Avant toute commande, recueille ces entrées :

- type demandé : **Agent**, **Application** ou **Module** ;
- organisation et identifiant exact de la cible ;
- environnement exact (`sandbox`, `development`, `integration_test`,
  `staging` ou `production`) ;
- chemin du projet Agent Spec ou du Module ;
- contexte MauriceCLI explicite et endpoint MCP explicite si le parcours
  passe par MCP ;
- test plan déclaré, s'il existe, et son emplacement dans le projet.

Ne déduis jamais une cible depuis son nom affiché. Ne lis jamais un fichier de
jeton et ne demande jamais de secret dans le chat. Un changement de contexte
CLI ne rebranche pas le serveur MCP : après un changement de cible, invalide
les références, plans et hashes précédents, puis refais le préflight.

Pour la porte MCP locale, la commande publique est :

```text
maurice doctor --mcp-endpoint <endpoint> --mcp-token-file <private-token-file> --json
```

Doctor prouve uniquement le handshake et le catalogue accessibles. Il ne
prouve ni l'authentification métier, ni un droit d'apply, ni un Workflow
exécuté. Lis `mcp_frontdoor.checked` et `mcp_frontdoor.ok` sans afficher le
jeton.

Une connexion d'authoring se prépare depuis le bootstrap MCP `amb_` et sa
configuration retournée, avec ses headers de contrat. Ce bootstrap ne se passe
ni à `maurice agent connect` (qui attend `amc_`), ni à `maurice assistant
connect` (front door). Réutilise la connexion autorisée ; ne fabrique pas un
bootstrap d'organisation ou un droit plus large pour réparer une portée Agent.
Pour connaître le contrat MCP, utilise `inception_mcp_capabilities` ou les
outils déjà chargés dans le client ; `inception_tools_list` inventorie les
outils runtime d'un Agent et ne prouve pas la présence du catalogue org-builder.

## Choisir le rail

### Nouvel Agent

Un nouvel Agent commence par le graphe d'architecture. Utilise les outils MCP
réels suivants, ou l'interface Studio si elle est demandée :

```text
inception_architecture_observe
inception_architecture_plan
inception_architecture_plan_get
inception_architecture_apply
inception_architecture_verify
```

`inception_architecture_plan` exige `operations` et produit un plan
immuable valable 24 heures. Une opération peut déclarer `create_agent` dans
le plan. Le plan ne crée rien et ne s'approuve pas lui-même.

Exemple de formes d'appel MCP (les valeurs viennent du contexte et du contrat
retournés par le serveur) :

```json
{
  "organization_id": "<organization-id>",
  "operations": [
    {
      "op": "create_agent",
      "client_ref": "<client-ref>",
      "display_name": "<display-name>",
      "agent_alias": "<agent-alias>",
      "environment_name": "development",
      "goal": {
        "id": "<goal-id>",
        "title": "<goal-title>",
        "description": "<goal-description>",
        "success_criteria": "<success-criteria>",
        "source": "<goal-source>"
      }
    }
  ]
}
```

Pour appliquer le plan d'architecture, l'appel exact doit contenir les trois
champs suivants :

```json
{
  "organization_id": "<organization-id>",
  "plan_id": "<architecture-plan-id>",
  "plan_hash": "<architecture-plan-hash>",
  "approval_id": "<server-approval-id>"
}
```

Le plan expire 24 heures après sa création ; conserve et contrôle son
`expires_at`. Pour un plan dont toutes les opérations sont `create_agent` et
dont l'environnement est `sandbox`, `development` ou `integration_test`, le
serveur peut retourner une approbation de policy. Les autres combinaisons
peuvent demander une décision humaine. Dans les deux cas, l'agent ne fabrique
jamais d'`approval_id` et ne peut pas appeler l'outil d'approbation à la place
d'une personne. Après un apply accepté, `inception_architecture_verify` doit
confirmer le graphe et les écarts. Une réponse d'attente ou un plan expiré
arrête le parcours ; ne crée pas un second plan automatiquement.

Si `created_agents` contient l'identifiant mais que le suivi retourne
`authoring_required` (par exemple un handoff Studio sans `instance_url`),
l'Agent existe déjà. Ne recrée ni plan ni Agent et ne relance pas l'apply
pour réparer le lien. Rapporte le suivi incomplet et reprends l'authoring du
même Agent, avec un contexte autorisé : `spec init --agent-id <created-id>
--organization <org-id> --env <env> --agent-alias <alias> --dir <new-path>`.
Ce scaffold ne déploie aucun Workflow ; un Agent `draft` n'est pas une
livraison runtime. Si une Spec distante existe, utilise `spec pull`.

La commande CLI publique de préparation d'architecture est :

```text
maurice architecture plan --file <operations.json> \
  [--organization <organization-id>] --json
```

Le fichier doit être un objet JSON contenant un tableau `operations`. Le plan
est ensuite relu avec `architecture plan-get`, approuvé par le principal
humain et appliqué avec le `plan_hash` et l'`approval_id` exacts. Ne confonds
pas ce rail avec `maurice build plan`, qui prépare un plan Agent Spec.

### Agent existant

Pour un Agent existant, `spec init` prépare les fichiers locaux d'authoring ;
il ne crée aucun Agent distant :

```text
maurice spec init \
  --env <env> --agent-alias <alias> --dir <path> --json
```

Les options de ciblage disponibles sont `--dir`, `--env`, `--agent-alias`,
`--agent-id`, `--organization` et `--title`. Lorsque le serveur renvoie le
statut `existing` parce que la spec existe déjà à distance, `init` s'arrête
avec un conflit et indique d'utiliser `spec pull` :

```text
maurice spec pull --env <env> --agent-alias <alias> --dir <path> --json
```

### Application

Une Application est une ressource distante distincte d'un Agent Spec. Sa
création exige une autorisation explicite :

```text
maurice app init <applicationKey> \
  --organization <organization-id> \
  --kind <kind> \
  [--name <display-name>] \
  [--description <description>] \
  [--auth-connector-deployment <deployment-id>] --json
```

`<kind>` vaut `standard` ou `test`. Le plan et l'apply Application sont
séparés du rail Agent Spec :

```text
maurice app plan <applicationId> --organization <organization-id> \
  [--out <plan.json>] --json

maurice app apply <applicationId> --organization <organization-id> \
  [--plan <plan.json>] [--plan-hash <approved-plan-hash>] \
  [--tests <tests-mode>] [--run-tests] --json
```

`<tests-mode>` vaut `auto`, `on` ou `off`.

Ne présente pas l'Application comme créée ou livrée avant le résultat de
l'apply et sa vérification de livraison. Consulte [Application delivery](../../agentmaurice/references/app-delivery.md)
pour les preuves attendues.

### Module

Un Module est un paquet versionné de Workflows, MiniApps ou schémas. Son
scaffold est local et ne crée ni Agent ni Application :

```text
maurice module init <moduleKey> [--dir <path>] [--version <version>] --json
maurice module validate --file <path>/module.yaml --json
maurice module test --file <path>/module.yaml --json
```

`--file` désigne directement le fichier `module.yaml` (chemin relatif au
répertoire courant ou chemin absolu) ; il n'existe pas d'option `--project`.
`module validate` et `module test` valident le manifeste local. Ils ne
exécutent pas un Workflow déployé et ne remplacent pas le test plan de
l'Agent consommateur.

Le cycle canonique est `validate -> test -> publish/import -> ajout à la
desired state -> plan -> approbation humaine -> apply --tests auto -> verify`.
La publication est une mutation externe : elle nécessite une autorisation
explicite séparée et ne doit pas être lancée par ce raccourci sans demande.

## Rail Agent Spec : check, plan, apply, verify

Avant `check`, lis les fichiers du projet, le lock, l'environnement, les
Workflows/MiniApps, la provenance Git et le fichier de test plan déclaré. Le
chemin usuel du test plan est `agents/<alias>/tests/test-plan.json`.
Si le client ne peut pas lire ces fichiers, arrête avant le plan et indique
la permission de lecture manquante. Un check distant positif ne remplace pas
la lecture du projet. Utilise les chemins déclarés avec l’outil de lecture ;
un listing shell ou un accès au répertoire parent n’est pas nécessaire.

### Check

Commande exacte :

```text
maurice spec check \
  --env <env> --agent-alias <alias> --dir <path> --json
```

Options : `--agent-id`, `--organization`, `--offline`,
`--warnings-as-errors`, `--pull-request-url`. Le succès doit retourner des
contrats locaux valides et une validation distante positive. Avec `--offline`,
le résultat ne prouve que les contrats embarqués et le workspace local.

Arrête le parcours si les contrats sont invalides, si les warnings sont
bloquants, si la cible est ambiguë, si le lock ou la provenance ne correspond
plus, ou si le test plan dont la qualification est demandée est absent ou invalide.
Sans test plan déclaré, conserve les alternatives explicites de `build test`
(smoke Workflow, contrôle Module ou relecture d’une preuve), sans prétendre
avoir rejoué un test plan.

### Plan

Commande exacte :

```text
maurice spec plan \
  --env <env> --agent-alias <alias> --dir <path> --json
```

Options : `--agent-id`, `--organization`, `--out <plan.json>`,
`--pull-request-url`, `--git-sandbox`. Le résultat attendu contient un
`plan_id`, un `plan_hash`, les préconditions de version, la provenance Git, la
politique de tests, le risque et le blast radius. Conserve exactement cet
artefact ; ne recalcule pas le plan à l'étape suivante.

Un plan expiré, périmé, en conflit ou déjà associé à une autre cible arrête le
parcours. Il faut alors pull/merge/rebase, refaire `check`, puis produire un
nouveau plan et une nouvelle autorisation serveur : policy approval ou
approbation humaine distincte si le plan retourne `awaiting_approval`.

### Approbation

Si le serveur retourne `awaiting_approval`, le client Claude présente le plan
et s'arrête. Si le serveur retourne une approbation de policy, il conserve
l'`approval_id` et le `plan_hash` associés. Dans aucun cas il ne doit appeler
`inception_agent_spec_approve` ou `spec approve`, ni inventer ou réutiliser un
`approval_id`.

Une autorisation de policy valide et une demande explicite d'apply permettent
de continuer sans demander une confirmation humaine supplémentaire. La CLI
peut relire elle-même l'`approval_id` du plan persistant si l'option est omise.
Cela ne crée aucune approbation et ne remplace jamais `awaiting_approval`.

Après la décision humaine ou l'autorisation de policy, reprends le même `plan_id` et vérifie que le
`plan_hash` approuvé correspond exactement à l'artefact local. Une approbation
ne prouve pas que l'apply ou les tests ont réussi.

### Apply

Commande exacte :

```text
maurice spec apply \
  --plan <plan-id> --dir <path> \
  [--approval-id <server-approval-id>] \
  --tests auto --idempotency-key <stable-operation-key> --json
```

Options exactes supplémentaires : `--target <registered-vm-context>`,
`--mandate <mandate-id>`, `--evidence kind=ref` (répétable),
`--tests <tests-mode>` (valeurs `auto`, `on` ou `off`), `--skip-reason
<reason>`, `--git-sandbox`.

`--approval-id` et `--mandate` sont mutuellement exclusifs. Un mandat est une
admission serveur limitée par sa portée, son expiry, ses quotas et ses
preuves ; il n'est pas une approbation automatique inventée par l'agent.
`--tests off` est interdit en production et exige `--skip-reason` hors
production. Utilise `--tests auto` pour exécuter le test plan attaché au plan.

La façade `maurice build apply` reprend ce rail mais exige explicitement
`--plan <plan-id-ou-fichier>` et `--tests on`. `maurice build test` impose les
mêmes deux paramètres ; il sert à qualifier le test plan du plan approuvé.
Un plan absent ou `--tests auto|off` sont refusés avant l'appel serveur.

Arrête sur `approval_required`, `approval_plan_mismatch`, une cible non
prouvée, un plan stale, une admission de mandat refusée, une erreur d'apply ou
un test bloquant. Un code nul avant `verify` ne suffit pas pour annoncer une
livraison.

### Verify

Commande exacte :

```text
maurice spec verify \
  --plan <plan-id> --dir <path> --wait --json
```

Le résultat attendu contient `verified: true`, aucun drift bloquant, l'état
runtime attendu, la provenance et les tests réussis. `failed`, `verified:
false`, un drift ou une preuve incomplète est un échec ; ne le reformule pas en
succès.

Le parcours combiné `maurice spec deploy` existe et accepte `--tests
<tests-mode>` (valeurs `auto`, `on` ou `off`), `--plan-only`, `--no-wait` et
`--pull-request-url`. Il reste
équivalent à check → plan → gate d'approbation → apply → verify ; il ne doit
pas masquer l'identité du plan ou de l'approbateur dans le rapport.

## Équivalents MCP réels

Le client peut exposer les noms ci-dessous directement, ou un catalogue à
chargement différé avec `inception_search` et `inception_call`. Dans ce second
cas, cherche le schéma avec `inception_search({"tool_name":"<nom>"})`, puis
appelle `inception_call({"tool_name":"<nom>","arguments":{...}})`. Utilise
exactement les outils effectivement chargés et leurs paramètres. Ce dispatch
conserve la portée et les gates serveur ; il ne crée aucun droit et ne rend
pas disponible une opération absente du catalogue autorisé.


Les outils `inception_agent_spec_*` sont la surface d'authoring. Ils acceptent
des fichiers `{path, content}` et exigent le contrat client et le hash du
bundle pour les mutations. Utilise `inception_mcp_capabilities` ou le catalogue
MCP connecté pour obtenir le `contract_bundle_sha256` courant ; ne le devine
pas.

### Init, check et plan

Formes minimales :

```json
{
  "agent_alias": "<alias>",
  "title": "<title>",
  "client_contract": "agent-authoring/v2",
  "contract_bundle_sha256": "<bundle-sha256>"
}
```

Pour `inception_agent_spec_check`, ajoute `files` et, si nécessaire,
`organization_id`, `environment_name` et `source_control` :

```json
{
  "organization_id": "<organization-id>",
  "agent_alias": "<alias>",
  "environment_name": "<env>",
  "files": [{"path": "<relative-path>", "content": "<file-content>"}],
  "source_control": {
    "commit_sha": "<commit>",
    "workspace_hash": "<workspace-hash>"
  }
}
```

`inception_agent_spec_plan` exige aussi `base_resource_version` et une
provenance `source_control` contenant au minimum `commit_sha` et
`workspace_hash`. Il retourne l'artefact immuable, le hash et la politique de
tests. `inception_agent_spec_workflow_preview` peut compiler et exécuter un
Workflow draft en sandbox ; il ne l'enregistre pas dans un runtime managed.

### Apply et verify

`inception_agent_spec_apply` exige :

```json
{
  "plan_id": "<plan-id>",
  "plan_hash": "<plan-hash>",
  "idempotency_key": "<stable-operation-key>",
  "client_contract": "agent-authoring/v2",
  "contract_bundle_sha256": "<bundle-sha256>",
  "approval_id": "<server-approval-id>",
  "tests": "auto"
}
```

Le serveur accepte à la place `mandate_id` avec `evidence` structurée ;
`approval_id` et `mandate_id` ne se combinent pas. Les refus typés
`mandate_missing`, `mandate_expired`, `mandate_scope_denied`,
`effect_class_not_auto`, `mandate_limit_exceeded` et `evidence_missing`
laissent le plan préparé et exigent une décision adaptée.

`inception_agent_spec_verify` exige `plan_id` et reste en lecture seule :

```json
{"organization_id": "<organization-id>", "plan_id": "<plan-id>"}
```

### Architecture nouvelle

Les équivalents MCP d'un nouveau Agent sont `inception_architecture_observe`,
`inception_architecture_plan`, `inception_architecture_plan_get`,
`inception_architecture_apply` et `inception_architecture_verify`.
`inception_architecture_plan` exige `operations`; `apply` exige exactement
`plan_id`, `plan_hash` et `approval_id`. L'agent ne peut pas produire cette
approbation.

### Front door de consommation

La surface publique `maurice` est distincte de l'authoring :

```text
maurice.search(query, kind[])
maurice.explain(ref, input?)
maurice.execute(ref, input, idempotency_key, expected_plan_hash?)
```

Elle découvre et exécute une capacité déjà exposée par un Workflow. Elle ne
crée ni Agent, ni Application, ni Agent Spec, et ne remplace pas
`inception_agent_spec_plan/apply/verify`. Après `search`, conserve la
référence exacte, fais `explain`, puis exécute seulement avec le même
`idempotency_key` et, si disponible, `expected_plan_hash`. `pending` est une
attente humaine ; `rejected` arrête le parcours.

## Tests : plan déclaré et test unitaire séparé

### Test plan déclaré

Le test plan fait partie de la spec consommatrice, pas d'un Module. Valide son
contrat avec :

```text
maurice spec schema test-plan --json
```

`maurice spec apply --tests auto` exécute le test plan attaché pendant le
premier apply du plan. Il ne constitue pas un invocateur autonome de test plan.
Si le plan est déjà terminal, un appel avec la même clé d'idempotence retourne
le résultat mémorisé (`replayed: true`) et ne rejoue aucun cas. Une autre clé
sur un plan déjà appliqué est refusée ; ne change pas la clé pour contourner
le cache ou forcer un second run.

Pour une demande explicite « build test » avec un test plan déclaré, la voie
publique est une requalification bornée :

1. lire le projet et exécuter `maurice spec check` ;
2. annoncer qu'un nouveau plan immuable, sans modification de desired state,
   sera préparé uniquement pour rejouer le test plan ;
3. exécuter `maurice spec plan` et présenter son `plan_id`, `plan_hash`, sa
   politique et son `expires_at` ;
4. attendre l'autorisation serveur prévue par la policy ou une approbation
   humaine distincte ;
5. après cette gate, exécuter `maurice spec apply --tests auto` avec une
   nouvelle clé stable propre à ce run, puis `maurice spec verify --wait` ;
6. rapporter `test_run_id`, nombre de cas, statut, erreurs et preuve de
   vérification.

Un champ de diff `modified` n'impose pas à lui seul une nouvelle décision
humaine. Compare les valeurs avant/après et le `spec_hash` : si les empreintes
sont identiques, toutes les valeurs sont égales et aucune ligne de contenu
n'est ajoutée ou retirée, rapporte cette projection vide. La gate d'apply
reste exactement celle du plan serveur. Une version incrémentée pour la
requalification n'est pas une modification de contenu.

Après des appels séparés `apply` puis `verify`, le lock local peut rester à
l'ancienne version. Avant le prochain plan, un refus `agent_spec_plan_stale`
exige une synchronisation par `spec pull`, puis revue, commit et nouveau check.
Ne réécris jamais le lock à la main ; préserve toute modification locale
avant ce pull.

La préparation (lecture, check et plan) est autorisée par l'intention
explicite « build test » ; l'apply reste derrière sa gate. Si le serveur
refuse un plan sans changement, arrête et rapporte ce refus. Aucun nouveau
plan caché ou nouvelle API n'est inventé.

Il n'existe pas d'invocateur public V2 autonome supplémentaire pour rejouer un
test plan Agent Spec. `maurice test auto` exécute ses propres suites YAML
(hermetic/live/e2e) et ne remplace pas le test plan de l'Agent. N'appelle
aucune façade interne.

Sans test plan déclaré, le raccourci « build test » propose exactement l'une
de ces preuves, selon la demande : un smoke `maurice test workflow call`, le
contrôle local `maurice module test`, ou une preuve de test existante à relire.
Il ne prétend pas qu'un apply rejoué a exécuté de nouveaux cas.

### Test Workflow unitaire explicite

Pour un smoke ou un cas unitaire d'un Workflow déjà déployé dans un Agent de
test, utilise l'invocateur public dédié :

```text
maurice test workflow call <workflow-id> \
  --agent-id <integration-test-agent-id> \
  --input-file <input.json> --json
```

Options : `--organization <organization-id>`, `--runtime-url <workflow-url>`
et, à la place de `--input-file`, un ou plusieurs `--arg key=value`. Le JSON
d'entrée doit être un objet. Le résultat doit montrer une réponse HTTP 2xx,
`execution.state: completed` et `api_key_revoked: true`.

Ce test est une preuve séparée du test plan déclaré : rapporte son
`workflow-id`, son input non sensible, son état d'exécution et sa révocation
de clé, mais ne le présente jamais comme le replay de tous les cas du plan.
La commande ne crée ni ne déploie de Workflow.

Pour préparer un Agent d'intégration éphémère, le parcours public est :

```text
maurice test setup --fresh --save=false \
  --deployment-name <unique-name> --json
```

Suis ensuite le `next_command` renvoyé par le serveur ; n'invente pas un
identifiant d'Agent. Le nettoyage doit être explicite et vérifié avec la
commande publique indiquée par `test setup`.

## Sandbox, approbation et arrêts

- Le serveur autorise les opérations directes seulement dans les profils
  `sandbox`, `development` et `integration_test` lorsque le contrat l'indique.
  `staging`, `production` et les profils inconnus exigent le Workflow ou une
  approbation humaine distincte selon la politique serveur.
- Un sandbox unmanaged exige une demande explicite, un environnement non
  production, `management_mode: unmanaged` confirmé par le serveur, un Agent
  ciblé et l'absence de secret brut. Une ressource managed retourne vers le
  rail Agent Spec ; un flag sandbox ne contourne pas cette règle.
- `inception_agent_spec_workflow_preview` est un preview sandbox d'un draft et
  ne remplace pas `plan`, approval, `apply` ou `verify`.
- Ne lance jamais directement une mutation de Workflow/MiniApp managed avec
  `inception_*_definitions_*`; les mutations unmanaged doivent être
  explicitement déclarées comme telles par le serveur.
- Arrête sur cible absente ou ambiguë, endpoint non prouvé, contrat invalide,
  plan stale/expiré, hash différent, approbation absente ou révoquée, mandat
  refusé, test bloquant, drift ou vérification incomplète.

## Rapport attendu

Pour chaque étape, rapporte séparément : l'interface réellement appelée (CLI
ou outil MCP), la cible et l'environnement, la commande exacte, le code de
sortie ou le statut structuré, les identifiants `plan_id`/`plan_hash`/job si
retournés, les tests exécutés et la preuve de `verify`. Distingue toujours
raccordement, check, plan, décision humaine, apply, tests, verify, exécution
Workflow et qualification publique.

## Reprendre une Spec déjà initialisée

Une création d’Agent par plan d’architecture peut déjà initialiser sa Spec.
`build new agent` renvoie alors `remote_agent_spec_exists` ; conserver cet
Agent et utiliser le pull explicite, sans recommencer la création :

```text
maurice build pull --agent-id <agent-id> --agent-alias <alias> \
  --env <environment> --dir <project-directory> --json
```

Le profil local expose `maurice_build_pull` avec `dir`, `agent_id`,
`agent_alias` et `env`. L’opt-in `--allow-local-write` est nécessaire.
Aucun `force` n’est exposé par MCP : les modifications locales restent protégées.
Les paramètres de cible viennent du plan appliqué ou du contexte explicite.

Avant un appel du profil natif, lire `maurice_client_context` et comparer sa
cible publique avec l’intention. Pour un pull vers un dossier vide, les trois
paramètres `agent_id`, `agent_alias` et `env` sont obligatoires. Le serveur
fournit les fichiers et la classification ; ne pas fabriquer un fichier
d’environnement pour forcer une policy plus permissive.

## Résultat de `build test`

`build test --plan <id>` et `maurice_build_test` appliquent le plan autorisé
avec ses tests bloquants. Ils ne lancent pas un test plan arbitraire à part.
Un même plan et une même clé retrouvent une preuve existante : si `replayed`
vaut `true`, rapporte « résultat de test existant », son statut et son run ID ;
ne dis jamais que tu viens de relancer les tests. Pour une nouvelle campagne,
prépare un nouveau plan au même état vérifié puis exécute ses tests bloquants.
La clé implicite native est déterministe sur le plan et son autorisation.

| CLI | MCP natif |
|---|---|
| build new module/application/agent | maurice_build_new_module/application/agent |
| build pull/check/plan | maurice_build_pull/check/plan |
| build apply/test/verify | maurice_build_apply/test/verify |
| architecture observe/plan/plan-get/apply | maurice_architecture_observe/plan/plan_get/apply |

Le schéma de chaque outil fixe ses champs ; ne passe pas d’argv libres.
Le contexte est vérifié avant l’appel. Une erreur `client_target_changed`
impose de reconnecter explicitement le profil ; ne modifie pas une cible
pour faire passer le contrôle.
