# From an Application Description Directory

Use this when the user already has a repository folder that describes the application in text and wants the AI to use that material as the source of truth.

## Prompt

```text
Use $agentmaurice to build this application from the description directory in this repository.
Read the directory first and treat it as the source of truth for the app structure.
Model the application as one or more deployments with one or more meta-recette blueprints.
Ask only blocking questions.
Build the first useful slice, preview and verify it, then prepare deployment on AgentMaurice.
Return the application map, the deployed slice, the access path, and the next slices to implement.
```

## Expected Flow

```text
1. Read the application description directory
2. Extract deployments, blueprint slices, and runtime modes
3. workspace_session_list()
4. workspace_bootstrap_contract(session_id="...", goal="create_meta_recette|create_recipe")
5. workspace_current_state()
6. Prepare the first slice
7. Preview or verify it
8. Present the plan
9. Apply after approval
10. Return the application map and next steps
```
