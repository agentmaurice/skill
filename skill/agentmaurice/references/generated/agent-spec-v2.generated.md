# Agent Spec V2 — contrats embarqués

> Généré par `tools/contract_tool.py`. Ne pas modifier à la main.

Bundle SHA-256 : `f6381fe3022dcfa59ad96366a25a9816c0e5660e15caeeb15e7ce3ca74a684cc`

Charge le schéma ou l'exemple exact avec `maurice spec schema <contrat>` et
`maurice spec example <contrat>`. Les copies ci-dessous sont validées à chaque génération.

| Contrat | Identifiant | Exemple validé |
|---|---|---|
| `project` | `agentmaurice.project/v2` | [`examples/project.json`](examples/project.json) (`1a64d1c76cd0878a56e37be2112491fac6185193a33817e5583234952d9c45f7`) |
| `environment` | `agentmaurice.environment/v2` | [`examples/environment.json`](examples/environment.json) (`d092cfba0d437b2c385053c5954dd262097c26649c6eb97a15e32fb421f0a595`) |
| `lock` | `agentmaurice.lock/v2` | [`examples/lock.json`](examples/lock.json) (`8dc246ba536d786813134e8f0b0c6aef19e09b38f3ae6187a6221363a1b6876a`) |
| `agent-spec` | `agentmaurice.agent_spec/v2` | [`examples/agent-spec.json`](examples/agent-spec.json) (`84ceaa709a6fd4c00875bd12b07171ba2d7905e601578d448517aac3e369f2de`) |
| `workflow` | `agentmaurice.workflow/v2` | [`examples/workflow.json`](examples/workflow.json) (`0030c48758e968d4b3e537b48985087b4e4b83cfb055d3e0ca0938b69a72c48f`) |
| `miniapp` | `agentmaurice.miniapp/v2` | [`examples/miniapp.json`](examples/miniapp.json) (`367d70ae0c7decba64506728addcd4f12e3088b3c81f3c6df10427126f86c009`) |
| `test-plan` | `agentmaurice.test_plan/v2` | [`examples/test-plan.json`](examples/test-plan.json) (`bde2a560c4ad6986b6bddfac4e6ca83945b83f2472a304d9e77c5f3167e50844`) |
| `bootstrap` | `agentmaurice.bootstrap/v2` | [`examples/bootstrap.json`](examples/bootstrap.json) (`0140826c525bf0b6578c3531eace034a99a13c3cce8b8a2456bada07d79017d3`) |
| `cli-error` | `agentmaurice.cli_error/v2` | [`examples/cli-error.json`](examples/cli-error.json) (`fc5e4aece83dc312d22bc7eecd9b4f08e44131512631b410e87f38358d7fe11e`) |

Le schéma embarqué est normatif. La référence Skill ne doit jamais inventer un champ
absent du schéma ni contourner `maurice spec check`.
Chaque objet `capabilities[]` de `agent-spec.json` doit désigner explicitement son
Workflow local avec `workflow_id`; aucune résolution par nom ou alias n'est autorisée.
