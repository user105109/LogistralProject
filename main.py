from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok"}

from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional

class Position(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    device_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime
    accuracy: Optional[float] = None
    speed: Optional[float] = None

class StorePosition(SQLModel):
    device_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime
    accuracy: Optional[float] = None
    speed: Optional[float] = None

DATABASE_URL = "sqlite:///gps.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

@app.post("/position")
def create_position(camion_data: StorePosition):
    position = Position(**camion_data.model_dump())
    with Session(engine) as session:
        session.add(position)
        session.commit()
        session.refresh(position)
    return position