from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    start_date: Mapped[datetime | None] = mapped_column(Date)
    end_date: Mapped[datetime | None] = mapped_column(Date)
    capacity: Mapped[int | None] = mapped_column(Integer)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    created_by: Mapped["User"] = relationship("User", back_populates="events_created")
    donations: Mapped[list["Donation"]] = relationship(
        "Donation", back_populates="event"
    )
    documents: Mapped[list["Document"]] = relationship(
        "Document", back_populates="event"
    )

    def __repr__(self) -> str:
        return f"Event(id={self.id}, name={self.name})"

