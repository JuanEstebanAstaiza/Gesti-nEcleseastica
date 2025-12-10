from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base para todos los modelos ORM."""


__all__ = ["Base"]

