# Agent Spec V2 — contrats embarqués

> Généré par `tools/contract_tool.py`. Ne pas modifier à la main.

Bundle SHA-256 : `f4e473842c62bcefc179800e6d2b30b4cedd2a55bf5c74df909365fc6fbc3ceb`

Charge le schéma ou l'exemple exact avec `maurice spec schema <contrat>` et
`maurice spec example <contrat>`. Les copies ci-dessous sont validées à chaque génération.

| Contrat | Identifiant | Exemple validé |
|---|---|---|
| `project` | `agentmaurice.project/v2` | [`examples/project.json`](examples/project.json) (`1a64d1c76cd0878a56e37be2112491fac6185193a33817e5583234952d9c45f7`) |
| `environment` | `agentmaurice.environment/v2` | [`examples/environment.json`](examples/environment.json) (`6249b1dec781406f897453b28c5f0ff654cc70db5c1f54f2681688cc622d7285`) |
| `lock` | `agentmaurice.lock/v2` | [`examples/lock.json`](examples/lock.json) (`8dc246ba536d786813134e8f0b0c6aef19e09b38f3ae6187a6221363a1b6876a`) |
| `agent-spec` | `agentmaurice.agent_spec/v2` | [`examples/agent-spec.json`](examples/agent-spec.json) (`84ceaa709a6fd4c00875bd12b07171ba2d7905e601578d448517aac3e369f2de`) |
| `workflow` | `agentmaurice.workflow/v2` | [`examples/workflow.json`](examples/workflow.json) (`3d26544c4ea44dce925338af49bae7f3cb4308ec397e77016c815d3a75abe345`) |
| `miniapp` | `agentmaurice.miniapp/v2` | [`examples/miniapp.json`](examples/miniapp.json) (`367d70ae0c7decba64506728addcd4f12e3088b3c81f3c6df10427126f86c009`) |
| `test-plan` | `agentmaurice.test_plan/v2` | [`examples/test-plan.json`](examples/test-plan.json) (`bde2a560c4ad6986b6bddfac4e6ca83945b83f2472a304d9e77c5f3167e50844`) |
| `bootstrap` | `agentmaurice.bootstrap/v2` | [`examples/bootstrap.json`](examples/bootstrap.json) (`0140826c525bf0b6578c3531eace034a99a13c3cce8b8a2456bada07d79017d3`) |
| `cli-error` | `agentmaurice.cli_error/v2` | [`examples/cli-error.json`](examples/cli-error.json) (`fc5e4aece83dc312d22bc7eecd9b4f08e44131512631b410e87f38358d7fe11e`) |

Le schéma embarqué est normatif. La référence Skill ne doit jamais inventer un champ
absent du schéma ni contourner `maurice spec check`.
Chaque objet `capabilities[]` de `agent-spec.json` doit désigner explicitement son
Workflow local avec `workflow_id`; aucune résolution par nom ou alias n'est autorisée.
