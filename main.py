from fastapi import FastAPI, HTTPException
app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from fastapi.responses import FileResponse

@app.get("/app")
def serve_app():
    return FileResponse("index.html")

from sqlmodel import SQLModel, Field, create_engine, Session, select
from datetime import datetime, timezone, timedelta
from typing import Optional
import uuid
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

class Position(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # default wud cause duplicating ids, but default_factory is perfect cuz it runs the func fresh each time a neew pos is created
    device_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime
    accuracy: Optional[float] = Field(default=None, ge=0)
    speed: Optional[float] = Field(default=None, ge=0)

DATABASE_URL = "sqlite:///gps.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

@app.post("/position")
def create_position(position: Position):
    try:
        if not (-90 <= position.latitude <= 90):
            raise ValueError("Latitude hors limites")
        if not (-180 <= position.longitude <= 180):
            raise ValueError("Longitude hors limites")
        if position.accuracy is not None and position.accuracy < 0:
            raise ValueError("Accuracy est toujours positive")
        if position.speed is not None and position.speed < 0:
            raise ValueError("Speed est toujours positive")

        if isinstance(position.timestamp, str):
            position.timestamp = datetime.fromisoformat( position.timestamp )
        if position.timestamp.tzinfo is None:
            position.timestamp = position.timestamp.replace( tzinfo=timezone.utc )

        time_now = datetime.now(timezone.utc)
        if position.timestamp > time_now + timedelta(minutes=5):
            raise HTTPException(status_code=422, detail="Le temps est dans le future")
        if position.timestamp < time_now - timedelta(days=1):
            raise HTTPException(status_code=422, detail="Le temps est tres ancien (> 1j)")

        with Session(engine) as session:
            last_pos_stmt = select(Position).where(
                Position.device_id == position.device_id
            ).order_by(Position.timestamp.desc())
            last_pos = session.exec(last_pos_stmt).first()

            if last_pos:
                last_ts = last_pos.timestamp
                if last_ts.tzinfo is None:
                    last_ts = last_ts.replace(tzinfo=timezone.utc)
                elapsed_sec = (position.timestamp - last_ts).total_seconds()

                if elapsed_sec > 0:
                    dist_km = ((position.latitude - last_pos.latitude) ** 2 +
                               (position.longitude - last_pos.longitude) ** 2) ** 0.5 * 111
                    implied_speed_kmh = (dist_km / elapsed_sec) * 3600

                    if implied_speed_kmh > 200:
                        logger.error(
                            f"Position aberrante detectee: appareil={position.device_id} "
                            f"vitesse impliquee={implied_speed_kmh:.1f} km/h - rejetee"
                        )
                        raise HTTPException(
                            status_code=422,
                            detail=f"Position rejetee: deplacement implique {implied_speed_kmh:.1f} km/h, jugee irrealiste"
                        )
                    
            session.add(position)
            session.commit()
            session.refresh(position)
        logger.info(f"Position enregistree: appareil: {position.device_id} id={position.id} latitude={position.latitude} longitude={position.longitude}")
        return position
    except ValueError as e:
        logger.error(f"Position rejetee pour l'appareil {position.device_id}: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Impossible d'enregistrer la position de l'appareil {position.device_id}: {e}")
        raise

@app.get("/position/{device_id}")
def get_last_stored_pos(device_id: str):
    with Session(engine) as session:
        stmt = select(Position).where(Position.device_id == device_id).order_by(Position.timestamp.desc())
        pos = session.exec(stmt).first()
        if not pos:
            raise HTTPException(status_code=404, detail="Aucune position trouvee pour cet appareil")
        now = datetime.now(timezone.utc)
        ts = pos.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        store_now_elapsed = (now - ts).total_seconds()

        if store_now_elapsed > 120:
            status = "hors_ligne"
        elif store_now_elapsed > 15:
            status = "signal_interrompu"
        elif pos.accuracy is not None and pos.accuracy > 20:
            status = "signal_faible"
        else:
            status = "en_ligne"

        result = pos.model_dump()
        result["status"] = status
        return result

@app.get("/history/{device_id}")
def get_history(device_id: str, start: datetime = None, end: datetime = None):
    with Session(engine) as session:
        stmt = select(Position).where(Position.device_id == device_id)

        if start:
            stmt = stmt.where(Position.timestamp >= start)
        if end:
            stmt = stmt.where(Position.timestamp <= end)

        stmt = stmt.order_by(Position.timestamp.asc())
        positions = session.exec(stmt).all()

        if not positions:
            raise HTTPException(status_code=404, detail="Aucune position dans cette periode")

        return positions












        return pos