"""
Rutas de administración de la iglesia - Solo para admins del tenant
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas.church import (
    ChurchConfigUpdate, ChurchConfigRead,
    LiveStreamCreate, LiveStreamUpdate, LiveStreamRead,
    PublicContentCreate, PublicContentUpdate, PublicContentRead,
    AnnouncementCreate, AnnouncementUpdate, AnnouncementRead
)
from app.core.tenant import get_tenant_db, require_tenant
from app.core.deps import require_admin
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["church-admin"])


# ============== Configuración de Iglesia ==============

@router.get("/config", response_model=ChurchConfigRead)
async def get_church_config(
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Obtiene la configuración completa de la iglesia"""
    result = await session.execute(text("SELECT * FROM church_config LIMIT 1"))
    config = result.fetchone()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    return ChurchConfigRead(
        id=config.id,
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
        bank_info=config.bank_info,
        paypal_email=config.paypal_email,
        donation_link=config.donation_link,
        service_schedule=config.service_schedule,
        updated_at=config.updated_at
    )


@router.patch("/config", response_model=ChurchConfigRead)
async def update_church_config(
    data: ChurchConfigUpdate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza la configuración de la iglesia"""
    import json
    
    # Construir query dinámico
    updates = []
    params = {}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            # Serializar listas y dicts a JSON para PostgreSQL
            if isinstance(value, (list, dict)):
                params[field] = json.dumps(value)
            else:
                params[field] = value
            updates.append(f'"{field}" = :{field}')
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    updates.append("updated_at = NOW()")
    
    result = await session.execute(
        text(f"UPDATE church_config SET {', '.join(updates)} WHERE id = 1 RETURNING *"),
        params
    )
    config = result.fetchone()
    await session.commit()
    
    if not config:
        raise HTTPException(status_code=404, detail="Configuración no encontrada")
    
    return ChurchConfigRead(
        id=config.id,
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
        bank_info=config.bank_info,
        paypal_email=config.paypal_email,
        donation_link=config.donation_link,
        service_schedule=config.service_schedule,
        updated_at=config.updated_at
    )


# ============== Transmisiones en Vivo ==============

@router.get("/streams", response_model=list[LiveStreamRead])
async def list_streams(
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Lista todas las transmisiones"""
    result = await session.execute(
        text("SELECT * FROM live_streams ORDER BY created_at DESC")
    )
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


@router.post("/streams", response_model=LiveStreamRead, status_code=status.HTTP_201_CREATED)
async def create_stream(
    data: LiveStreamCreate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Crea una nueva transmisión"""
    result = await session.execute(
        text("""
            INSERT INTO live_streams (title, description, stream_url, youtube_video_id, 
                facebook_video_id, platform, is_live, is_featured, scheduled_at, thumbnail_url, created_by_id)
            VALUES (:title, :description, :stream_url, :youtube_video_id, 
                :facebook_video_id, :platform, :is_live, :is_featured, :scheduled_at, :thumbnail_url, :created_by_id)
            RETURNING *
        """),
        {
            "title": data.title,
            "description": data.description,
            "stream_url": data.stream_url,
            "youtube_video_id": data.youtube_video_id,
            "facebook_video_id": data.facebook_video_id,
            "platform": data.platform,
            "is_live": data.is_live,
            "is_featured": data.is_featured,
            "scheduled_at": data.scheduled_at,
            "thumbnail_url": data.thumbnail_url,
            "created_by_id": current_user.id
        }
    )
    stream = result.fetchone()
    await session.commit()
    
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


@router.patch("/streams/{stream_id}", response_model=LiveStreamRead)
async def update_stream(
    stream_id: int,
    data: LiveStreamUpdate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza una transmisión"""
    updates = []
    params = {"id": stream_id}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            updates.append(f"{field} = :{field}")
            params[field] = value
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    result = await session.execute(
        text(f"UPDATE live_streams SET {', '.join(updates)} WHERE id = :id RETURNING *"),
        params
    )
    stream = result.fetchone()
    await session.commit()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Transmisión no encontrada")
    
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


@router.post("/streams/{stream_id}/go-live", response_model=LiveStreamRead)
async def start_live_stream(
    stream_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Inicia una transmisión en vivo"""
    result = await session.execute(
        text("""
            UPDATE live_streams 
            SET is_live = TRUE, started_at = NOW() 
            WHERE id = :id 
            RETURNING *
        """),
        {"id": stream_id}
    )
    stream = result.fetchone()
    await session.commit()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Transmisión no encontrada")
    
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


@router.post("/streams/{stream_id}/end-live", response_model=LiveStreamRead)
async def end_live_stream(
    stream_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Finaliza una transmisión en vivo"""
    result = await session.execute(
        text("""
            UPDATE live_streams 
            SET is_live = FALSE, ended_at = NOW() 
            WHERE id = :id 
            RETURNING *
        """),
        {"id": stream_id}
    )
    stream = result.fetchone()
    await session.commit()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Transmisión no encontrada")
    
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


@router.delete("/streams/{stream_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_stream(
    stream_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Elimina una transmisión"""
    await session.execute(
        text("DELETE FROM live_streams WHERE id = :id"),
        {"id": stream_id}
    )
    await session.commit()
    return None


# ============== Contenido Público ==============

@router.get("/content", response_model=list[PublicContentRead])
async def list_content(
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Lista todo el contenido"""
    result = await session.execute(
        text("SELECT * FROM public_content ORDER BY updated_at DESC")
    )
    contents = result.fetchall()
    
    return [PublicContentRead(
        id=c.id,
        slug=c.slug,
        title=c.title,
        content=c.content,
        excerpt=c.excerpt,
        content_type=c.content_type,
        featured_image_url=c.featured_image_url,
        is_published=c.is_published,
        is_featured=c.is_featured,
        published_at=c.published_at,
        meta_title=c.meta_title,
        meta_description=c.meta_description,
        created_at=c.created_at,
        updated_at=c.updated_at
    ) for c in contents]


@router.post("/content", response_model=PublicContentRead, status_code=status.HTTP_201_CREATED)
async def create_content(
    data: PublicContentCreate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Crea nuevo contenido"""
    result = await session.execute(
        text("""
            INSERT INTO public_content (slug, title, content, excerpt, content_type,
                featured_image_url, is_published, is_featured, meta_title, meta_description,
                published_at, created_by_id)
            VALUES (:slug, :title, :content, :excerpt, :content_type,
                :featured_image_url, :is_published, :is_featured, :meta_title, :meta_description,
                CASE WHEN :is_published THEN NOW() ELSE NULL END, :created_by_id)
            RETURNING *
        """),
        {
            **data.model_dump(),
            "created_by_id": current_user.id
        }
    )
    content = result.fetchone()
    await session.commit()
    
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


@router.patch("/content/{content_id}", response_model=PublicContentRead)
async def update_content(
    content_id: int,
    data: PublicContentUpdate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza contenido existente"""
    updates = ["updated_at = NOW()"]
    params = {"id": content_id}
    
    for field, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            updates.append(f"{field} = :{field}")
            params[field] = value
    
    result = await session.execute(
        text(f"UPDATE public_content SET {', '.join(updates)} WHERE id = :id RETURNING *"),
        params
    )
    content = result.fetchone()
    await session.commit()
    
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


@router.delete("/content/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Elimina contenido"""
    await session.execute(
        text("DELETE FROM public_content WHERE id = :id"),
        {"id": content_id}
    )
    await session.commit()
    return None


# ============== Gestión de Eventos ==============

@router.get("/events")
async def list_admin_events(
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Lista todos los eventos (vista admin) con conteo de registrados"""
    result = await session.execute(
        text("""
            SELECT e.id, e.name, e.description, e.start_date, e.end_date, e.start_time, e.end_time,
                   e.location, e.capacity, e.is_public, e.is_featured, e.image_url, e.created_at,
                   COALESCE(COUNT(r.id) FILTER (WHERE NOT r.is_cancelled), 0) as registered_count
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            GROUP BY e.id
            ORDER BY e.start_date DESC
        """)
    )
    events = result.fetchall()
    
    return [{
        "id": e.id,
        "name": e.name,
        "description": e.description,
        "start_date": e.start_date.isoformat() if e.start_date else None,
        "end_date": e.end_date.isoformat() if e.end_date else None,
        "start_time": str(e.start_time) if e.start_time else None,
        "end_time": str(e.end_time) if e.end_time else None,
        "location": e.location,
        "capacity": e.capacity,
        "registered_count": e.registered_count,
        "is_public": e.is_public,
        "is_featured": e.is_featured,
        "image_url": e.image_url,
        "created_at": e.created_at.isoformat() if e.created_at else None
    } for e in events]


def parse_date(date_str):
    """Convierte string a objeto date"""
    if not date_str:
        return None
    if isinstance(date_str, str):
        from datetime import datetime as dt
        try:
            return dt.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except:
            try:
                return dt.strptime(date_str, '%Y-%m-%d').date()
            except:
                return None
    return date_str


def parse_time(time_str):
    """Convierte string a objeto time"""
    if not time_str:
        return None
    if isinstance(time_str, str):
        from datetime import datetime as dt
        try:
            return dt.strptime(time_str, '%H:%M:%S').time()
        except:
            try:
                return dt.strptime(time_str, '%H:%M').time()
            except:
                return None
    return time_str


@router.post("/events", status_code=status.HTTP_201_CREATED)
async def create_admin_event(
    data: dict,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Crea un nuevo evento"""
    result = await session.execute(
        text("""
            INSERT INTO events (name, description, start_date, end_date, start_time, end_time,
                location, capacity, is_public, is_featured, image_url, created_by_id)
            VALUES (:name, :description, :start_date, :end_date, :start_time, :end_time,
                :location, :capacity, :is_public, :is_featured, :image_url, :created_by_id)
            RETURNING id, name, description, start_date, end_date, start_time, end_time,
                location, capacity, is_public, is_featured, image_url, created_at
        """),
        {
            "name": data.get("name"),
            "description": data.get("description"),
            "start_date": parse_date(data.get("start_date")),
            "end_date": parse_date(data.get("end_date")),
            "start_time": parse_time(data.get("start_time")),
            "end_time": parse_time(data.get("end_time")),
            "location": data.get("location"),
            "capacity": data.get("capacity"),
            "is_public": data.get("is_public", True),
            "is_featured": data.get("is_featured", False),
            "image_url": data.get("image_url"),
            "created_by_id": current_user.id
        }
    )
    event = result.fetchone()
    await session.commit()
    
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_date": event.start_date.isoformat() if event.start_date else None,
        "end_date": event.end_date.isoformat() if event.end_date else None,
        "start_time": str(event.start_time) if event.start_time else None,
        "end_time": str(event.end_time) if event.end_time else None,
        "location": event.location,
        "capacity": event.capacity,
        "is_public": event.is_public,
        "is_featured": event.is_featured,
        "image_url": event.image_url,
        "created_at": event.created_at.isoformat() if event.created_at else None
    }


@router.patch("/events/{event_id}")
async def update_admin_event(
    event_id: int,
    data: dict,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Actualiza un evento existente"""
    updates = []
    params = {"id": event_id}
    
    allowed_fields = ["name", "description", "start_date", "end_date", "start_time", 
                      "end_time", "location", "capacity", "is_public", "is_featured", "image_url"]
    
    date_fields = ["start_date", "end_date"]
    time_fields = ["start_time", "end_time"]
    
    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = :{field}")
            value = data[field]
            # Parsear fechas y horas
            if field in date_fields:
                value = parse_date(value)
            elif field in time_fields:
                value = parse_time(value)
            params[field] = value
    
    if not updates:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    
    result = await session.execute(
        text(f"""
            UPDATE events SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, name, description, start_date, end_date, start_time, end_time,
                location, capacity, is_public, is_featured, image_url, created_at
        """),
        params
    )
    event = result.fetchone()
    await session.commit()
    
    if not event:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    return {
        "id": event.id,
        "name": event.name,
        "description": event.description,
        "start_date": event.start_date.isoformat() if event.start_date else None,
        "end_date": event.end_date.isoformat() if event.end_date else None,
        "start_time": str(event.start_time) if event.start_time else None,
        "end_time": str(event.end_time) if event.end_time else None,
        "location": event.location,
        "capacity": event.capacity,
        "is_public": event.is_public,
        "is_featured": event.is_featured,
        "image_url": event.image_url,
        "created_at": event.created_at.isoformat() if event.created_at else None
    }


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_admin_event(
    event_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Elimina un evento"""
    await session.execute(
        text("DELETE FROM events WHERE id = :id"),
        {"id": event_id}
    )
    await session.commit()
    return None


# ============== Anuncios ==============

@router.get("/announcements", response_model=list[AnnouncementRead])
async def list_announcements(
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Lista todos los anuncios"""
    result = await session.execute(
        text("SELECT * FROM announcements ORDER BY priority DESC, created_at DESC")
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


@router.post("/announcements", response_model=AnnouncementRead, status_code=status.HTTP_201_CREATED)
async def create_announcement(
    data: AnnouncementCreate,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Crea un nuevo anuncio"""
    result = await session.execute(
        text("""
            INSERT INTO announcements (title, content, announcement_type, priority,
                is_public, start_date, end_date, created_by_id)
            VALUES (:title, :content, :announcement_type, :priority,
                :is_public, :start_date, :end_date, :created_by_id)
            RETURNING *
        """),
        {
            **data.model_dump(),
            "created_by_id": current_user.id
        }
    )
    announcement = result.fetchone()
    await session.commit()
    
    return AnnouncementRead(
        id=announcement.id,
        title=announcement.title,
        content=announcement.content,
        announcement_type=announcement.announcement_type,
        priority=announcement.priority,
        is_public=announcement.is_public,
        is_active=announcement.is_active,
        start_date=announcement.start_date,
        end_date=announcement.end_date,
        created_at=announcement.created_at
    )


@router.delete("/announcements/{announcement_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_announcement(
    announcement_id: int,
    session: AsyncSession = Depends(get_tenant_db),
    current_user: User = Depends(require_admin)
):
    """Elimina un anuncio"""
    await session.execute(
        text("DELETE FROM announcements WHERE id = :id"),
        {"id": announcement_id}
    )
    await session.commit()
    return None

