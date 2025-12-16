"""Schemas para configuración de iglesia y contenido público"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


# ============== Church Config ==============

class ChurchConfigUpdate(BaseModel):
    church_name: str | None = None
    slogan: str | None = None
    description: str | None = None
    about_us: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None
    history: str | None = None
    
    # Contacto
    address: str | None = None
    city: str | None = None
    country: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    
    # Branding
    logo_url: str | None = None
    cover_image_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    
    # Redes sociales
    social_facebook: str | None = None
    social_instagram: str | None = None
    social_youtube: str | None = None
    social_twitter: str | None = None
    social_tiktok: str | None = None
    
    # Donaciones
    donation_info: str | None = None
    bank_info: dict | None = None
    paypal_email: str | None = None
    donation_link: str | None = None
    
    # Horarios
    service_schedule: list | dict | None = None


class ChurchConfigRead(BaseModel):
    id: int
    church_name: str
    slogan: str | None
    description: str | None
    about_us: str | None
    mission: str | None
    vision: str | None
    values: str | None
    history: str | None
    address: str | None
    city: str | None
    country: str | None
    phone: str | None
    email: str | None
    website: str | None
    logo_url: str | None
    cover_image_url: str | None
    primary_color: str
    secondary_color: str
    social_facebook: str | None
    social_instagram: str | None
    social_youtube: str | None
    social_twitter: str | None
    social_tiktok: str | None
    donation_info: str | None
    bank_info: dict | None
    paypal_email: str | None
    donation_link: str | None
    service_schedule: list | dict | None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChurchPublicInfo(BaseModel):
    """Info pública de la iglesia (sin datos sensibles)"""
    church_name: str
    slogan: str | None
    description: str | None
    about_us: str | None
    mission: str | None
    vision: str | None
    values: str | None
    history: str | None
    address: str | None
    city: str | None
    country: str | None
    phone: str | None
    email: str | None
    website: str | None
    logo_url: str | None
    cover_image_url: str | None
    primary_color: str
    secondary_color: str
    social_facebook: str | None
    social_instagram: str | None
    social_youtube: str | None
    social_twitter: str | None
    social_tiktok: str | None
    donation_info: str | None
    donation_link: str | None
    service_schedule: list | dict | None

    model_config = ConfigDict(from_attributes=True)


# ============== Live Streams ==============

class LiveStreamCreate(BaseModel):
    title: str
    description: str | None = None
    stream_url: str | None = None
    youtube_video_id: str | None = None
    facebook_video_id: str | None = None
    platform: str = "youtube"
    is_live: bool = False
    is_featured: bool = False
    scheduled_at: datetime | None = None
    thumbnail_url: str | None = None


class LiveStreamUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    stream_url: str | None = None
    youtube_video_id: str | None = None
    facebook_video_id: str | None = None
    platform: str | None = None
    is_live: bool | None = None
    is_featured: bool | None = None
    scheduled_at: datetime | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    thumbnail_url: str | None = None


class LiveStreamRead(BaseModel):
    id: int
    title: str
    description: str | None
    stream_url: str | None
    youtube_video_id: str | None
    facebook_video_id: str | None
    platform: str
    is_live: bool
    is_featured: bool
    scheduled_at: datetime | None
    started_at: datetime | None
    ended_at: datetime | None
    thumbnail_url: str | None
    view_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== Public Content ==============

class PublicContentCreate(BaseModel):
    slug: str
    title: str
    content: str | None = None
    excerpt: str | None = None
    content_type: str = "page"
    featured_image_url: str | None = None
    is_published: bool = True
    is_featured: bool = False
    meta_title: str | None = None
    meta_description: str | None = None


class PublicContentUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    excerpt: str | None = None
    content_type: str | None = None
    featured_image_url: str | None = None
    is_published: bool | None = None
    is_featured: bool | None = None
    meta_title: str | None = None
    meta_description: str | None = None


class PublicContentRead(BaseModel):
    id: int
    slug: str
    title: str
    content: str | None
    excerpt: str | None
    content_type: str
    featured_image_url: str | None
    is_published: bool
    is_featured: bool
    published_at: datetime | None
    meta_title: str | None
    meta_description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============== Announcements ==============

class AnnouncementCreate(BaseModel):
    title: str
    content: str | None = None
    announcement_type: str = "general"
    priority: int = 0
    is_public: bool = True
    start_date: datetime | None = None
    end_date: datetime | None = None


class AnnouncementUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    announcement_type: str | None = None
    priority: int | None = None
    is_public: bool | None = None
    is_active: bool | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class AnnouncementRead(BaseModel):
    id: int
    title: str
    content: str | None
    announcement_type: str
    priority: int
    is_public: bool
    is_active: bool
    start_date: datetime | None
    end_date: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

