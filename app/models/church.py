"""
Modelos específicos de cada iglesia (tenant database)
"""
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChurchConfig(Base):
    """Configuración de la iglesia - editable por admin"""
    __tablename__ = "church_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    church_name: Mapped[str] = mapped_column(String(255), nullable=False)
    slogan: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    about_us: Mapped[str | None] = mapped_column(Text)
    mission: Mapped[str | None] = mapped_column(Text)
    vision: Mapped[str | None] = mapped_column(Text)
    values: Mapped[str | None] = mapped_column(Text)
    history: Mapped[str | None] = mapped_column(Text)
    
    # Contacto
    address: Mapped[str | None] = mapped_column(Text)
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255))
    
    # Branding
    logo_url: Mapped[str | None] = mapped_column(String(500))
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    primary_color: Mapped[str] = mapped_column(String(7), default="#8b5cf6")
    secondary_color: Mapped[str] = mapped_column(String(7), default="#06b6d4")
    
    # Redes sociales
    social_facebook: Mapped[str | None] = mapped_column(String(255))
    social_instagram: Mapped[str | None] = mapped_column(String(255))
    social_youtube: Mapped[str | None] = mapped_column(String(255))
    social_twitter: Mapped[str | None] = mapped_column(String(255))
    social_tiktok: Mapped[str | None] = mapped_column(String(255))
    
    # Información de donación
    donation_info: Mapped[str | None] = mapped_column(Text)
    bank_info: Mapped[dict | None] = mapped_column(JSONB)
    paypal_email: Mapped[str | None] = mapped_column(String(255))
    donation_link: Mapped[str | None] = mapped_column(String(500))
    
    # Horarios
    service_schedule: Mapped[dict | None] = mapped_column(JSONB)  # {"sunday": ["9:00 AM", "11:00 AM"], ...}
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class LiveStream(Base):
    """Transmisiones en vivo de misas y eventos"""
    __tablename__ = "live_streams"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # URLs de streaming
    stream_url: Mapped[str | None] = mapped_column(String(500))
    youtube_video_id: Mapped[str | None] = mapped_column(String(50))
    facebook_video_id: Mapped[str | None] = mapped_column(String(100))
    
    # Plataforma principal
    platform: Mapped[str] = mapped_column(String(50), default="youtube")  # youtube, facebook, custom
    
    # Estado
    is_live: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Programación
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Media
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    
    # Metadatos
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    created_by: Mapped["User"] = relationship("User")


class PublicContent(Base):
    """Contenido público personalizable (páginas, anuncios, etc.)"""
    __tablename__ = "public_content"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    excerpt: Mapped[str | None] = mapped_column(String(500))
    
    # Tipo de contenido
    content_type: Mapped[str] = mapped_column(String(50), default="page")  # page, announcement, blog
    
    # Media
    featured_image_url: Mapped[str | None] = mapped_column(String(500))
    
    # Estado
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # SEO
    meta_title: Mapped[str | None] = mapped_column(String(255))
    meta_description: Mapped[str | None] = mapped_column(String(500))
    
    # Metadatos
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    created_by: Mapped["User"] = relationship("User")


class Announcement(Base):
    """Anuncios y noticias de la iglesia"""
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    
    # Tipo y prioridad
    announcement_type: Mapped[str] = mapped_column(String(50), default="general")  # general, urgent, event
    priority: Mapped[int] = mapped_column(Integer, default=0)
    
    # Visibilidad
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Programación
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Metadatos
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    created_by: Mapped["User"] = relationship("User")


# Forward reference para evitar import circular
from app.models.user import User

