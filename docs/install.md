# Installer Maurice dans Codex ou Claude Code

Les plugins connectés sont distribués prêts à installer depuis le catalogue
GitHub AgentMaurice. Le connecteur est inclus : aucun build, installation
séparée de MauriceCLI ou fichier de configuration à éditer.

## Codex

Ajouter le catalogue une fois, puis installer Maurice :

```bash
codex plugin marketplace add agentmaurice/skill --ref plugins
codex plugin add maurice@agentmaurice
```

Dans Desktop, ouvrir un nouveau chat du projet choisi avec le plugin activé.
Respecter l’éventuelle demande native de rechargement du client ; ne pas
redémarrer les autres sessions pour activer un test.

## Claude Code

Dans Claude Code :

```text
/plugin install maurice --marketplace agentmaurice/skill#plugins
```

Choisir la portée d’installation proposée par le client. Pour un essai,
choisir uniquement ce projet pour soi. Suivre la demande native de
rechargement éventuelle ; elle dépend de la version du client.

## Connecter son One

1. Demander : **Connecte Maurice à mon One.** Le parcours est aussi disponible
   avec `$setup` dans Codex ou `/maurice:setup` dans Claude Code.
2. Donner l’adresse de l’accueil de One si aucune cible n’a encore été
   enregistrée. Vérifier le client, le nom et l’adresse affichés.
3. Ouvrir le lien retourné et comparer le code. Dans One, choisir la portée
   et les droits, puis **Autoriser la connexion** ou **Refuser**. La lecture
   seule est proposée par défaut ; exécuter un Workflow nécessite un choix
   explicite. L’ouverture peut demander la connexion One habituelle.
4. Revenir au chat et demander de vérifier la connexion. Le plugin effectue
   uniquement des lectures. Une autorisation donnée n’est pas encore une
   preuve de connexion ; le contrôle doit réussir.

Chaque client conserve sa propre autorisation privée. Les chats suivants la
réutilisent. Dans One, **Réglages → Brancher mon assistant** permet de la
révoquer ; les droits et approbations métier restent vérifiés côté serveur.
Un refus, une expiration ou une révocation arrêtent le parcours, sans autre
cible ou secret de secours.

## Compatibilité et versions

Le One doit prendre en charge `agentmaurice.assistant_pairing/v1`. Un ancien
One demande une mise à jour compatible ; le plugin ne le reconstruit pas et
n’ouvre aucun port entrant. Les paquets contiennent des exécutables natifs
pour macOS arm64/amd64, Linux arm64/amd64 et Windows amd64. La disponibilité
et les limites effectivement qualifiées sont publiées avec la release.

Le catalogue `plugins` est généré par la CI depuis un commit intégré à `main`.
Chaque release `plugin-v…` conserve les deux archives, leurs SHA-256 et
`release.json`, avec le commit source. Les instructions de construction ne
font pas partie du parcours d’installation.

Le connecteur est un client de One : ce paquet ne distribue pas le runtime
One et ne donne aucun droit supplémentaire sur l’instance.

Les anciens parcours explicites CLI, External Inception et le packaging de
développement sont conservés dans [l’installation avancée](advanced-install.md).
