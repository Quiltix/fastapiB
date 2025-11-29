from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

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


async def update_event(db: AsyncSession, event_id: int, schema: schemas.EventUpdate, user_id: int) -> models.Event:
    """
    Обновляет данные мероприятия.
    """
    event_to_update = await get_by_id(db, event_id=event_id)

    if not event_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие не найдено."
        )

    if event_to_update.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на редактирование этого мероприятия."
        )

    update_data = schema.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(event_to_update, key, value)

    db.add(event_to_update)
    await db.commit()
    await db.refresh(event_to_update)

    updated_event = await get_by_id(db, event_id=event_to_update.id)
    return updated_event


async def get_by_id(db: AsyncSession, event_id: int) -> models.Event | None:
    """Получает мероприятие по ID с предзагрузкой данных о владельце и билетах."""
    query = (
        select(models.Event)
        .where(models.Event.id == event_id)
        .options(
            joinedload(models.Event.owner),
            joinedload(models.Event.tickets)
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().first()


async def get_events_by_owner(db: AsyncSession, owner_id: int) -> List[models.Event]:
    """
    Получает список всех мероприятий, созданных указанным пользователем.
    """
    query = (
        select(models.Event)
        .where(models.Event.owner_id == owner_id)
        .options(
            joinedload(models.Event.owner)
            )
        )
    result = await db.execute(query)
    return result.scalars().unique().all()

async def get_all_active_events(db: AsyncSession) -> List[models.Event]:
    """
    Получает список всех мероприятий, созданных указанным пользователем.
    """
    query = (
        select(models.Event)
        .where(models.Event.start_time > datetime.now())
        .options(
            joinedload(models.Event.owner)
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().all()

async def get_old_events(db: AsyncSession) -> List[models.Event]:
    """
    Получает список всех мероприятий, созданных указанным пользователем.
    """
    query = (
        select(models.Event)
        .where(models.Event.start_time <= datetime.now())
        .options(
            joinedload(models.Event.owner)
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().all()