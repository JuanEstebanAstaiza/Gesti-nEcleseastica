from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class RegistrationCreate(BaseModel):
    attendee_name: str
    attendee_email: str
    notes: str | None = None


class RegistrationRead(BaseModel):
    id: int
    event_id: int
    attendee_name: str
    attendee_email: str
    notes: str | None = None
    is_cancelled: bool = False
    registered_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

