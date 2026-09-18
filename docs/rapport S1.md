# Rapport de tests — Semaine 1

Zouhair Messoudi — Stage Logistral

## Ce que j'ai fait cette semaine

J'ai fait la base : un simulateur qui envoie des positions GPS (lat, long, timestamp, accuracy, speed) à une API FastAPI, qui vérifie les données et les enregistre dans une base SQLite.

Stack : FastAPI + SQLModel + SQLite. Pas de frontend encore, c'est prévu semaine 2.

## Tests faits

| Test | Attendu | Obtenu | OK ? |
|---|---|---|---|
| Position valide complète | 200, enregistrée | 200, avec un id (UUID) | oui |
| device_id manquant | 422 | 422 | oui |
| latitude = 999 | 422 | 422 (après correction) | oui |
| longitude = -222 | 422 | 422 (après correction) | oui |
| accuracy négative | 422 | 422 (après correction) | oui |
| speed négative | 422 | 422 (après correction) | oui |
| timestamp bizarre ("hier") | 422 | 422 | oui |
| timestamp vieux de 3 jours | 422 | 422 | oui |
| timestamp dans le futur | 422 | 422 | oui |
| accuracy/speed absents | 200, null | 200, null | oui |
| Coupure réseau | le simulateur crash pas, reprend tout seul | ok, testé en coupant puis relançant uvicorn | oui |
| Envoi continu plusieurs minutes | pas de perte/doublon | à retester sur plus longtemps | à refaire |

## Les problèmes que j'ai eu

**1. SQLModel avec table=True qui valide pas correctement**

Ça, ça m'a pris le plus de temps. J'avais mis des règles de validation sur les champs (genre `Field(ge=-90, le=90)` pour la latitude, un `field_validator` pour le timestamp) et ça marchait pas du tout. N'importe quoi passait, même latitude = 999.

Après avoir cherché, j'ai compris que quand une classe SQLModel sert aussi de table (avec `table=True`), elle valide pas vraiment comme une classe normale le ferait. C'est pas écrit clairement dans la doc, j'ai mis du temps à piger que mon code avait l'air bon mais s'exécutait juste jamais.

Ce que j'ai fait : j'ai mis toute la validation à la main direct dans la fonction de l'endpoint, avant d'enregistrer. Ça marche mais c'est moins propre. Faudra peut-être revenir à deux classes séparées (une pour valider, une pour la table) comme au début.

**2. Bug bête dans les logs**

J'avais fait une faute de frappe dans le format du logger (`%levelname)s` au lieu de `%(levelname)s`), ça faisait planter le logging à chaque erreur. Corrigé.

**3. Le timestamp qui passait pas au début**

SQLite voulait pas enregistrer le timestamp parce qu'il arrivait en texte (string) et pas en vrai objet datetime Python. Réglé en le convertissant à la main dans l'endpoint.

## Ce qui manque encore

- Pas d'endpoint pour l'historique (prévu semaine 2)
- Pas de gestion si deux positions arrivent avec le même timestamp
- Le test "envoi continu longtemps" pas encore fait sérieusement
- Pas d'authentification sur l'API (pas demandé pour l'instant)

## Pour la semaine prochaine

- Endpoint pour avoir la dernière position d'un device (presque fait)
- Page HTML simple avec Tailwind + carte Leaflet
- Historique par période