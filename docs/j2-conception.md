# J2 — Conception

## Comment ça marche

Le simulateur (ou le téléphone) envoie une position GPS toutes les 5 secondes
à l'API. L'API vérifie que la position est correcte, et si oui, l'enregistre
dans la base SQLite. Si la position est bizarre (coordonnées impossibles,
date qui a pas de sens, etc.), elle est rejetée avec une erreur 422.

## Ce qu'on envoie comme position

| Champ | Type | Obligatoire | Règle |
|---|---|---|---|
| device_id | texte | oui | - |
| latitude | nombre | oui | entre -90 et 90 |
| longitude | nombre | oui | entre -180 et 180 |
| timestamp | date | oui | format ISO 8601, pas trop vieux ni dans le futur |
| accuracy | nombre | non | positif |
| speed | nombre | non | positif |

## Tests à faire

| Test | Entrée | Résultat attendu |
|---|---|---|
| Position normale | tout est correct | 200, position enregistrée |
| device_id manquant | device_id absent | 422 |
| latitude bizarre | latitude = 999 | 422 |
| longitude bizarre | longitude = -200 | 422 |
| accuracy négative | accuracy = -1 | 422 |
| speed négative | speed = -5 | 422 |
| timestamp cassé | timestamp = "hier" | 422 |
| timestamp trop vieux | plus de 24h | 422 |
| timestamp dans le futur | + de 5 min | 422 |
| accuracy/speed absents | pas grave, c'est optionnel | 200, valeurs vides |