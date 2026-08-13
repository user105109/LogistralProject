# GPS Tracker MVP — Logistral R&D

Prototype backend pour GPS position collection, validation, et storage.

## Setup
1. `python -m venv venv` + activate
2. `pip install fastapi uvicorn[standard] sqlalchemy pydantic `
3. `uvicorn main:app --reload`
4. Dans un terminal secondaire: `python gps_simu.py`

## Docs
Voir [docs/j2-conception.md](docs/j2-conception.md) pour l'architecture, model et test plan.

## Status
Semaine 1 en progrès
