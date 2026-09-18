# GPS Tracker — Prototype (Logistral)

Ça, c'est le prototype que j'ai développé pendant mon stage pour le module de
tracking GPS de Logistral. L'idée : un device (ou un simulateur pour l'instant)
envoie sa position, l'API la valide et la stocke, et on peut la voir sur une
carte en direct, avec un statut (en ligne / hors ligne / etc.) et un historique.

Le frontend est basique — c'était la consigne, vu qu'il sera refait plus tard
selon les besoins du client. Le travail sérieux est côté backend.

## Stack

- Backend : FastAPI + SQLModel + SQLite
- Frontend : HTML + Tailwind (CDN) + Leaflet.js pour la carte
- Simulateur : script Python qui fait semblant d'être un camion qui bouge,
  pour tester sans device réel

## Comment lancer le projet

```bash
python -m venv venv
pip install -r requirements.txt
uvicorn main:app --reload
```

Va sur `http://127.0.0.1:8000/app` pour voir la carte.

Optionnel, dans un deuxième terminal, pour simuler un camion qui bouge :
```bash
python gps_simu.py
```

Pour tester avec un vrai GPS (téléphone), il faut exposer le serveur en HTTPS
(par exemple avec ngrok : `ngrok http 8000`), puis ouvrir l'URL HTTPS + `/app`
sur le téléphone et cliquer sur "Activer GPS réel".

## Endpoints de l'API

| Méthode | URL | Ce que ça fait |
|---|---|---|
| GET | `/` | Vérifie que le serveur tourne |
| GET | `/app` | Sert la page avec la carte |
| POST | `/position` | Envoie une nouvelle position GPS |
| GET | `/position/{device_id}` | Dernière position connue + statut calculé |
| GET | `/history/{device_id}?start=...&end=...` | Historique, filtrable par date |

### Ce qu'on envoie pour une position

```json
{
  "device_id": "string",
  "latitude": "entre -90 et 90",
  "longitude": "entre -180 et 180",
  "timestamp": "format ISO 8601",
  "accuracy": "optionnel, doit être >= 0",
  "speed": "optionnel, doit être >= 0"
}
```

## Comment le statut est calculé

- en_ligne : dernière position il y a moins de 15 secondes
- signal_interrompu : entre 15 secondes et 2 minutes
- hors_ligne : plus de 2 minutes sans nouvelle position
- signal_faible : position récente mais accuracy > 20m

## Ce qui manque / limites connues

- Pas d'authentification sur l'API — pas demandé pour l'instant, mais à
  ajouter avant toute vraie utilisation
- Pas de pagination sur l'historique — pas un problème pour l'instant vu le
  volume de test
- Le calcul de distance dans l'historique est une approximation simple, pas
  un vrai calcul géodésique
- Pas de sélecteur de dates dans l'interface pour filtrer l'historique — le
  backend le supporte déjà (`start`/`end`), juste pas branché visuellement
- Testé avec un vrai téléphone via ngrok (pour le HTTPS, requis par le GPS du
  navigateur) plutôt qu'un vrai déploiement — en prod il faudrait un vrai
  hébergement, pas mon laptop

## Un souci technique qui m'a pris du temps

SQLModel, quand une classe a `table=True` (donc sert aussi de table de base
de données), n'applique pas toujours les validations Pydantic normalement
(les `Field(ge=..., le=...)` et les `field_validator`). J'ai perdu du temps à
comprendre pourquoi mes validations "avaient l'air correctes" mais servaient
à rien. Solution actuelle : je valide à la main dans la fonction de
l'endpoint, avant d'enregistrer en base. Détails dans le rapport de tests.

## Autres docs du projet

- [j2-conception.md](j2-conception.md) — architecture, modèle de données, plan de tests
- [rapport-tests-s1.md](rapport-tests-s1.md) — rapport de tests semaine 1

## Où j'en suis

Le flux complet marche de bout en bout : collecte → validation → stockage →
affichage sur carte → historique. C'est un prototype, pas un produit fini,
mais la base est solide et documentée.
