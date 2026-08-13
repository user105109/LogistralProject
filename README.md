# GPS Tracker MVP — Logistral R&D

Prototype backend for GPS position collection, validation, and storage.

## Setup
1. `python -m venv venv` + activate
2. `pip install -r requirements.txt`
3. `uvicorn main:app --reload`
4. In a second terminal: `python gps_simu.py` (simulates a device sending positions)

## Docs
See [docs/j2-conception.md](docs/j2-conception.md) for architecture, data model, and test plan.

## Status
Week 1 in progress — see project plan for milestones.