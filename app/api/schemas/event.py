from datetime import date
from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    name: str
    description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    capacity: int | None = None


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int
    created_by_id: int | None = None

    model_config = ConfigDict(from_attributes=True)

