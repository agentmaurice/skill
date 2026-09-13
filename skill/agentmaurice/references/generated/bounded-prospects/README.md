# Prospects — exemple Workflow V2 borné

Exemple déterministe du socle AGENT-298, sans appel LLM ni écriture métier.
`analyze-prospects` parcourt au plus 20 éléments déjà présents. Chaque
`route-prospect` choisit exactement une branche `new` ou `existing` ; toute
valeur inconnue produit `review`. Les branches ne font que projeter un résultat.
`input.json` produit exactement `expected.json`, dans le même ordre.

Les identifiants d'Agent et d'organisation sont des valeurs d'exemple. Copier
ce workspace dans un dépôt de test, puis le lier explicitement à un Agent de
test via le rail CLI disponible sur l'instance. Aucun identifiant d'exemple
ne doit être présenté comme un Agent existant. Après liaison, rejouer
`maurice spec check`, `plan`, les approbations exigées par le serveur, `apply`
puis `verify`, avec le même contrat et l'artefact exact du plan. Les fichiers
`input.json` et `expected.json` sont des données de recette, pas des Agent Specs.

Pour le contrôle statique sans instance :

```sh
maurice spec check --offline --dir . --env dev --agent-alias prospects
```

Une projection pure déclare `actions: []` et `output`. `output_schema` est
vérifié avant `completed`. Une liste vide retourne `results: []` ; un type
incorrect ou plus de 20 éléments échoue sans démarrer d'enfant. Le fallback
ne transmet que `child_input`, jamais le contexte complet implicite.

Un `llm_call` structuré peut calculer `prospect.kind` en amont ; il doit
fournir `llm_response_schema`. Cet exemple isole volontairement le choix et
la boucle de la disponibilité d'un provider. Il ne prouve ni le parcours One
AGENT-292, ni la publication de la Skill GitHub, ni l'alignement maurice-doc.
