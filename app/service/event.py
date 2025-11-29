from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import models
from app.schemas import schemas


async def create_event(db: AsyncSession, schema: schemas.EventCreate, user_id: int) -> models.Event:
    """Создает новое мероприятие в базе данных."""


    db_event = models.Event(
        **schema.model_dump(),
        owner_id=user_id
    )

    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)

    created_event = await get_by_id(db, event_id=db_event.id)

    return created_event
async def get_by_id(db: AsyncSession, event_id: int) -> models.Event | None:
    """Получает мероприятие по ID с предзагрузкой данных о владельце и билетах."""
    query = (
        select(models.Event)
        .where(models.Event.id == event_id)
        .options(
            selectinload(models.Event.owner),
            selectinload(models.Event.tickets)
        )
    )
    result = await db.execute(query)
    return result.scalars().first()