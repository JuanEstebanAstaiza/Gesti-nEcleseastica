"""
Rutas públicas de la iglesia - Sin autenticación requerida
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, text, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.church import (
    ChurchPublicInfo, LiveStreamRead, 
    PublicContentRead, AnnouncementRead
)
from app.api.schemas.event import EventRead
from app.core.tenant import get_tenant_db, require_tenant

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/config", response_model=ChurchPublicInfo)
async def get_church_info(
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant)
):
    """Obtiene la información pública de la iglesia"""
    result = await session.execute(
        text("""
            SELECT church_name, slogan, description, about_us, mission, vision, 
                   "values", history, address, city, country, phone, email, website,
                   logo_url, cover_image_url, primary_color, secondary_color,
                   social_facebook, social_instagram, social_youtube, social_twitter, social_tiktok,
                   donation_info, donation_link, service_schedule
            FROM church_config LIMIT 1
        """)
    )
    config = result.fetchone()
    
    if not config:
        # Retornar configuración por defecto
        return ChurchPublicInfo(
            church_name=tenant.get("name", "Mi Iglesia"),
            slogan=None,
            description=None,
            about_us=None,
            mission=None,
            vision=None,
            values=None,
            history=None,
            address=None,
            city=None,
            country=None,
            phone=None,
            email=None,
            website=None,
            logo_url=None,
            cover_image_url=None,
            primary_color="#8b5cf6",
            secondary_color="#06b6d4",
            social_facebook=None,
            social_instagram=None,
            social_youtube=None,
            social_twitter=None,
            social_tiktok=None,
            donation_info=None,
            donation_link=None,
            service_schedule=None
        )
    
    return ChurchPublicInfo(
        church_name=config.church_name,
        slogan=config.slogan,
        description=config.description,
        about_us=config.about_us,
        mission=config.mission,
        vision=config.vision,
        values=config.values,
        history=config.history,
        address=config.address,
        city=config.city,
        country=config.country,
        phone=config.phone,
        email=config.email,
        website=config.website,
        logo_url=config.logo_url,
        cover_image_url=config.cover_image_url,
        primary_color=config.primary_color,
        secondary_color=config.secondary_color,
        social_facebook=config.social_facebook,
        social_instagram=config.social_instagram,
        social_youtube=config.social_youtube,
        social_twitter=config.social_twitter,
        social_tiktok=config.social_tiktok,
        donation_info=config.donation_info,
        donation_link=config.donation_link,
        service_schedule=config.service_schedule
    )


@router.get("/events", response_model=list[EventRead])
async def get_public_events(
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant),
    upcoming: bool = Query(True, description="Solo eventos futuros"),
    limit: int = Query(10, ge=1, le=50)
):
    """Lista los eventos públicos de la iglesia"""
    query = """
        SELECT id, name, description, start_date, end_date, capacity, created_by_id
        FROM events 
        WHERE is_public = TRUE
    """
    
    if upcoming:
        query += " AND (start_date >= CURRENT_DATE OR start_date IS NULL)"
    
    query += " ORDER BY start_date ASC NULLS LAST LIMIT :limit"
    
    result = await session.execute(text(query), {"limit": limit})
    events = result.fetchall()
    
    return [EventRead(
        id=e.id,
        name=e.name,
        description=e.description,
        start_date=e.start_date,
        end_date=e.end_date,
        capacity=e.capacity,
        created_by_id=e.created_by_id
    ) for e in events]


@router.get("/events/{event_id}", response_model=EventRead)
async def get_public_event(
    event_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant)
):
    """Obtiene detalle de un evento público"""
    result = await session.execute(
        text("""
            SELECT id, name, description, start_date, end_date, capacity, created_by_id
            FROM events 
            WHERE id = :id AND is_public = TRUE
        """),
        {"id": event_id}
    )
    event = result.fetchone()
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    return EventRead(
        id=event.id,
        name=event.name,
        description=event.description,
        start_date=event.start_date,
        end_date=event.end_date,
        capacity=event.capacity,
        created_by_id=event.created_by_id
    )


@router.get("/streams", response_model=list[LiveStreamRead])
async def get_live_streams(
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant),
    live_only: bool = Query(False, description="Solo transmisiones en vivo"),
    limit: int = Query(10, ge=1, le=50)
):
    """Lista las transmisiones disponibles"""
    query = "SELECT * FROM live_streams WHERE 1=1"
    
    if live_only:
        query += " AND is_live = TRUE"
    
    query += " ORDER BY is_live DESC, scheduled_at DESC NULLS LAST, created_at DESC LIMIT :limit"
    
    result = await session.execute(text(query), {"limit": limit})
    streams = result.fetchall()
    
    return [LiveStreamRead(
        id=s.id,
        title=s.title,
        description=s.description,
        stream_url=s.stream_url,
        youtube_video_id=s.youtube_video_id,
        facebook_video_id=s.facebook_video_id,
        platform=s.platform,
        is_live=s.is_live,
        is_featured=s.is_featured,
        scheduled_at=s.scheduled_at,
        started_at=s.started_at,
        ended_at=s.ended_at,
        thumbnail_url=s.thumbnail_url,
        view_count=s.view_count,
        created_at=s.created_at
    ) for s in streams]


@router.get("/streams/live", response_model=LiveStreamRead | None)
async def get_current_live_stream(
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant)
):
    """Obtiene la transmisión en vivo actual (si existe)"""
    result = await session.execute(
        text("""
            SELECT * FROM live_streams 
            WHERE is_live = TRUE 
            ORDER BY is_featured DESC, started_at DESC 
            LIMIT 1
        """)
    )
    stream = result.fetchone()
    
    if not stream:
        return None
    
    return LiveStreamRead(
        id=stream.id,
        title=stream.title,
        description=stream.description,
        stream_url=stream.stream_url,
        youtube_video_id=stream.youtube_video_id,
        facebook_video_id=stream.facebook_video_id,
        platform=stream.platform,
        is_live=stream.is_live,
        is_featured=stream.is_featured,
        scheduled_at=stream.scheduled_at,
        started_at=stream.started_at,
        ended_at=stream.ended_at,
        thumbnail_url=stream.thumbnail_url,
        view_count=stream.view_count,
        created_at=stream.created_at
    )


@router.get("/content/{slug}", response_model=PublicContentRead)
async def get_public_content(
    slug: str,
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant)
):
    """Obtiene una página de contenido público por slug"""
    result = await session.execute(
        text("""
            SELECT id, slug, title, content, excerpt, content_type,
                   featured_image_url, is_published, is_featured, published_at,
                   meta_title, meta_description, created_at, updated_at
            FROM public_content 
            WHERE slug = :slug AND is_published = TRUE
        """),
        {"slug": slug}
    )
    content = result.fetchone()
    
    if not content:
        raise HTTPException(status_code=404, detail="Contenido no encontrado")
    
    return PublicContentRead(
        id=content.id,
        slug=content.slug,
        title=content.title,
        content=content.content,
        excerpt=content.excerpt,
        content_type=content.content_type,
        featured_image_url=content.featured_image_url,
        is_published=content.is_published,
        is_featured=content.is_featured,
        published_at=content.published_at,
        meta_title=content.meta_title,
        meta_description=content.meta_description,
        created_at=content.created_at,
        updated_at=content.updated_at
    )


@router.get("/announcements", response_model=list[AnnouncementRead])
async def get_public_announcements(
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant),
    limit: int = Query(5, ge=1, le=20)
):
    """Lista los anuncios públicos activos"""
    result = await session.execute(
        text("""
            SELECT id, title, content, announcement_type, priority,
                   is_public, is_active, start_date, end_date, created_at
            FROM announcements 
            WHERE is_public = TRUE 
              AND is_active = TRUE
              AND (start_date IS NULL OR start_date <= NOW())
              AND (end_date IS NULL OR end_date >= NOW())
            ORDER BY priority DESC, created_at DESC
            LIMIT :limit
        """),
        {"limit": limit}
    )
    announcements = result.fetchall()
    
    return [AnnouncementRead(
        id=a.id,
        title=a.title,
        content=a.content,
        announcement_type=a.announcement_type,
        priority=a.priority,
        is_public=a.is_public,
        is_active=a.is_active,
        start_date=a.start_date,
        end_date=a.end_date,
        created_at=a.created_at
    ) for a in announcements]


@router.get("/donation-info")
async def get_donation_info(
    session: AsyncSession = Depends(get_tenant_db),
    tenant: dict = Depends(require_tenant)
):
    """Obtiene la información de donaciones de la iglesia"""
    result = await session.execute(
        text("""
            SELECT church_name, donation_info, bank_info, paypal_email, donation_link
            FROM church_config LIMIT 1
        """)
    )
    config = result.fetchone()
    
    if not config:
        return {
            "church_name": tenant.get("name", "Mi Iglesia"),
            "donation_info": None,
            "payment_methods": []
        }
    
    payment_methods = []
    if config.bank_info:
        payment_methods.append({"type": "bank", "details": config.bank_info})
    if config.paypal_email:
        payment_methods.append({"type": "paypal", "email": config.paypal_email})
    if config.donation_link:
        payment_methods.append({"type": "online", "link": config.donation_link})
    
    return {
        "church_name": config.church_name,
        "donation_info": config.donation_info,
        "payment_methods": payment_methods
    }

