# app/service/ticket.py
from datetime import datetime, timezone
from typing import List

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

    new_ticket = models.Ticket(
        event_id=schema.event_id,
        participant_id=participant_id
    )

    db.add(new_ticket)
    await db.commit()
    created_ticket = await get_ticket_by_id(db, ticket_id=new_ticket.id)

    return created_ticket


async def cancel_registration(db: AsyncSession, ticket_id: int, user_id: int):

    ticket_to_delete = await get_ticket_by_id(db, ticket_id=ticket_id)

    if not ticket_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Регистрация (билет) не найдена."
        )
    if ticket_to_delete.participant_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав на отмену этой регистрации."
        )

    if ticket_to_delete.event.start_time < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно отменить регистрацию на уже прошедшее мероприятие."
        )

    # 5. Удаляем билет
    await db.delete(ticket_to_delete)
    await db.commit()


async def get_tickets_by_user_id(db: AsyncSession, user_id: int) -> List[models.Ticket]:
    """
    Получает список всех билетов, принадлежащих указанному пользователю.
    """
    query = (
        select(models.Ticket)
        .where(models.Ticket.participant_id == user_id)
        .options(
            joinedload(models.Ticket.event).options(
                joinedload(models.Event.owner)
            )
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().all()