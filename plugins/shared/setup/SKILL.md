---
name: setup
description: Connecter Maurice à votre One depuis Codex ou Claude Code, sans build, fichier à éditer ni secret à copier.
---

# Connecter Maurice à One

1. Appeler `maurice.connection_status`. Une connexion déjà vérifiée peut être réutilisée. Un fichier présent ne suffit pas à annoncer un succès.
2. Sans connexion, demander l’adresse de One une seule fois. Présenter toute cible déjà enregistrée et demander sa confirmation. Ne pas chercher de ports, lire les configurations d’autres assistants, choisir une autre instance ou inventer une adresse.
3. Appeler `maurice.connect` avec `one_url`. Présenter le nom et l’adresse du One, le client, le code de comparaison, l’expiration et le lien retournés. Ouvrir ce lien dans le navigateur si un outil autorisé le permet ; sinon donner le lien cliquable.
4. La personne saisit dans One le code de huit caractères affiché par son client, puis autorise ou refuse. Ne jamais approuver depuis le chat, saisir ce code ou cliquer le consentement à sa place, demander un jeton ou lire les fichiers privés du connecteur. Les droits affichés dans One font foi.
5. Appeler `maurice.connection_check` après la décision, en respectant l’intervalle annoncé. Sur attente, dire que One attend la décision ; ne pas lancer une boucle rapide. Sur refus ou expiration, arrêter. Une nouvelle demande nécessite un geste explicite de la personne.
6. Annoncer « Maurice est connecté à … » seulement si le contrôle retourne un succès vérifié avec découverte en lecture seule. Ne lancer aucun Workflow pour tester la connexion.

Une révocation (`grant_invalid`), une indisponibilité ou une incompatibilité restent des états distincts. Ne pas contourner un refus avec un autre jeton ou une autre cible. Si One ne prend pas en charge l’appairage, indiquer qu’une version compatible de One est requise ; ne pas proposer un build manuel ou une configuration cachée.

Après connexion, reprendre les instructions d’usage du plugin : `maurice.search` → `maurice.explain` → `maurice.execute`, référence exacte et idempotence. Les approbations métier restent sur One et distinctes de l’autorisation de connexion.
