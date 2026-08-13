# J2 — Conception

## Architecture (schéma)

[Simulateur GPS] --HTTP POST--> [API FastAPI] --> [Base SQLite]
                                      |
                                 [Validation Pydantic]

- Le simulateur envoie une position toutes les 5 secondes.
- L'API valide chaque position reçue (types, plages de valeurs).
- Une position valide est stockée dans SQLite ; une position invalide est rejetée (422).

## Modèle GPS (contrat de données)

| Champ      | Type     | Obligatoire | Contrainte           |
|------------|----------|-------------|-----------------------|
| device_id  | string   | oui         | -                      |
| latitude   | float    | oui         | -90 à 90               |
| longitude  | float    | oui         | -180 à 180             |
| timestamp  | datetime | oui         | format ISO 8601        |
| accuracy   | float    | non         | >= 0                   |
| speed      | float    | non         | >= 0                   |

## Plan de tests

| Cas de test                          | Entrée                              | Résultat attendu |
|---------------------------------------|--------------------------------------|-------------------|
| Position valide                       | Tous les champs corrects             | 200, position enregistrée avec id |
| device_id manquant                    | device_id absent                     | 422 |
| latitude hors limite                  | latitude = 999                       | 422 |
| longitude hors limite                 | longitude = -200                     | 422 |
| accuracy négative                     | accuracy = -1                        | 422 |
| speed négative                        | speed = -5                           | 422 |
| timestamp mal formé                   | timestamp = "hier"                   | 422 |
| Champs optionnels absents             | accuracy et speed absents            | 200, valeurs null en base |