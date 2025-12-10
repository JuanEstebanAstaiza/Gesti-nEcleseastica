from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class RegistrationCreate(BaseModel):
    event_id: int
    attendee_name: str
    attendee_email: str
    notes: str | None = None


class RegistrationRead(RegistrationCreate):
    id: int
    registered_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

