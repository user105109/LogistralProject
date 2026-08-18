# Rapport de tests — Semaine 1

Zouhair Messoudi — Stage

## Ce qui a été fait cette semaine (en retard)
J'ai mis en place la chaîne de base : un simulateur qui envoie des positions GPS
(latitude, longitude, timestamp, accuracy, speed) vers une API FastAPI, qui valide
les données et les enregistre dans une base SQLite.

Stack utilisée : FastAPI + SQLModel + SQLite, pas encore de frontend.

## Tests effectués

| Cas testé | Résultat attendu | Résultat obtenu | OK ? |
|---|---|---|---|
| Position complète et valide | 200, position enregistrée | 200, position enregistrée avec id (UUID) | oui |
| device_id manquant | 422 | 422 | oui |
| latitude = 999 | 422 | 422 (après correction, voir anomalies) | oui |
| longitude = -222 | 422 | 422 (après correction) | oui |
| accuracy négative | 422 | 422 (après correction) | oui |
| speed négative | 422 | 422 (après correction) | oui |
| timestamp mal formé ("hier") | 422 | 422 | oui |
| timestamp vieux de 3 jours | 422 | 422 | oui |
| timestamp dans le futur | 422 | 422 | oui |
| accuracy/speed absents (optionnels) | 200, valeurs null | 200, valeurs null | oui |
| Coupure réseau pendant l'envoi | le simulateur ne crash pas, reprend automatiquement | confirmé, testé en coupant uvicorn puis en le relançant | oui |
| Envoi en continu (simulateur, plusieurs minutes) | pas de perte, pas de doublons d'id | à re-tester sur une durée plus longue | à refaire

## Anomalies rencontrées

**1. SQLModel + table=True n'applique pas les validations Pydantic normalement**

C'était le plus gros blocage de la semaine. J'avais mis les contraintes de validation
directement sur les champs (ex: `Field(ge=-90, le=90)` pour la latitude, un
`field_validator` pour le timestamp), et ça ne marchait pas du tout — n'importe
quelle valeur passait, même des trucs absurdes genre latitude = 999.

Après pas mal de recherches j'ai compris que quand une classe SQLModel a
`table=True` (donc qu'elle sert aussi de table de base de données), elle ne
passe pas forcément par la validation Pydantic complète comme une classe
normale le ferait. C'est pas hyper documenté, j'ai mis du temps à comprendre
que le code "avait l'air correct" mais ne s'exécutait juste jamais.

Solution actuelle : j'ai déplacé toute la validation (coordonnées, timestamp)
directement dans la fonction de l'endpoint, à la main, avant d'enregistrer en
base. Ça marche, mais c'est moins propre que d'avoir la validation directement
sur le modèle. À voir si je change d'approche plus tard (peut-être remettre
deux classes séparées, une pour la validation et une pour la table, comme
au tout début).

**2. Bug de format dans les logs**

Petite erreur de frappe dans le format du logger (`%levelname)s` au lieu de
`%(levelname)s`) qui faisait planter le logging lui-même à chaque erreur.
Corrigé.

**3. Erreur de type sur le timestamp au tout début**

SQLite refusait d'enregistrer le timestamp parce qu'il arrivait encore sous
forme de texte (string) et pas de vrai objet datetime Python. Réglé avec une
conversion explicite dans l'endpoint.

## Limites connues / pas encore fait

- Pas de endpoint pour consulter l'historique (prévu J9, semaine 2)
- Pas de gestion des doublons si deux positions arrivent avec le même timestamp
- Le test "envoi en continu sur plusieurs minutes" n'a pas encore été fait sur une
  durée assez longue pour être vraiment concluant
- Pas encore de vraie authentification/sécurité sur l'API (pas demandé pour le
  prototype pour l'instant)

## Pour la semaine prochaine

- Endpoint GET pour récupérer la dernière position d'un device (presque fait)
- Page HTML simple avec Tailwind pour afficher la position sur une carte (Leaflet)
- Historique par période