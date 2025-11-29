# app/service/ticket.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from fastapi import HTTPException, status

from app.db import models
from app.schemas import schemas
from . import event as event_service


async def get_ticket_by_id(db: AsyncSession, ticket_id: int) -> models.Ticket | None:
    """Получает билет по ID с предзагрузкой связей."""
    query = (
        select(models.Ticket)
        .where(models.Ticket.id == ticket_id)
        .options(
            joinedload(models.Ticket.event),
            joinedload(models.Ticket.participant)
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().first()


async def get_ticket_by_event_and_participant(
        db: AsyncSession,
        event_id: int,
        participant_id: int
) -> models.Ticket | None:
    """Проверяет, существует ли уже билет для данного пользователя на данное мероприятие."""
    query = (
        select(models.Ticket)
        .where(
            models.Ticket.event_id == event_id,
            models.Ticket.participant_id == participant_id
        )
    )
    result = await db.execute(query)
    return result.scalars().first()


async def register_for_event(
        db: AsyncSession,
        schema: schemas.TicketCreate,
        participant_id: int
) -> models.Ticket:
    """Регистрирует пользователя на мероприятие (создает билет)."""
    # 1. Проверяем, существует ли мероприятие
    event = await event_service.get_by_id(db, event_id=schema.event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Мероприятие с таким ID не найдено."
        )

    existing_ticket = await get_ticket_by_event_and_participant(
        db, event_id=schema.event_id, participant_id=participant_id
    )
    if existing_ticket:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Вы уже зарегистрированы на это мероприятие."
        )

    # 3. Создаем билет
    new_ticket = models.Ticket(
        event_id=schema.event_id,
        participant_id=participant_id
    )

    db.add(new_ticket)
    await db.commit()
    created_ticket = await get_ticket_by_id(db, ticket_id=new_ticket.id)

    return created_ticket