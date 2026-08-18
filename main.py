from fastapi import FastAPI
app = FastAPI()

from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional
from pydantic import field_validator
import uuid

class Position(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    # default wud cause duplicating ids, but default_factory is perfect cuz it runs the func fresh each time a neew pos is created
    device_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    timestamp: datetime
    accuracy: Optional[float] = Field(default=None, ge=0)
    speed: Optional[float] = Field(default=None, ge=0)

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, raw_date):
        if isinstance(raw_date, str):
            return datetime.fromisoformat(raw_date)
        return raw_date

DATABASE_URL = "sqlite:///gps.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

@app.post("/position")
def create_position(position: Position):
    with Session(engine) as session:
        session.add(position)
        session.commit()
        session.refresh(position)
    return position