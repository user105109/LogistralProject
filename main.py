from fastapi import FastAPI, HTTPException
app = FastAPI()

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
            raise ValueError("Accuracy est tjrs positive")
        if position.speed is not None and position.speed < 0:
            raise ValueError("Speed est tjrs positive")

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
            session.add(position)
            session.commit()
            session.refresh(position)
        logger.info(f"Position enregistree: appareil: {position.device_id} id={position.id} latitude={position.latitude} longitude={position.longitude}")
        return position
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
        return pos