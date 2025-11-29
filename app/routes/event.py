# app/routers/events.py
from typing import List

from fastapi import APIRouter, status, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
from app.service import event as eventservice
from app.service.security import check_jwt

router = APIRouter(
    prefix="/events",
    tags=["events"]
)

@router.post(
    "",
    response_model=schemas.Event,
    status_code=status.HTTP_200_OK,
    summary="Создание нового мероприятия"
)
async def create_new_event(db: AsyncSession = Depends(get_db), schema: schemas.EventCreate = Body(...),user_id: int = Depends(check_jwt)):
    """
    Создает новое мероприятие. Доступно только для аутентифицированных пользователей.
"""
    event = await eventservice.create_event(db=db, schema=schema, user_id=user_id)
    return event

@router.patch("/{event_id}", response_model=schemas.Event, summary="Редактирование мероприятия"
)
async def update_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    schema: schemas.EventUpdate = Body(...),
    user_id: int = Depends(check_jwt),
):
    """
    Обновляет данные мероприятия по его ID.

    Доступно только для владельца мероприятия. Позволяет частично
    обновлять данные (например, можно прислать только `title`).
    """
    updated_event = await eventservice.update_event(db=db, event_id=event_id, schema=schema, user_id=user_id)
    return updated_event

@router.get("/active", response_model=List[schemas.Event], status_code=status.HTTP_200_OK, summary="Получение будущих мероприятия")
async def get_active_events(db: AsyncSession = Depends(get_db),user_id: int = Depends(check_jwt)):
    """
    Создает новое мероприятие. Доступно только для аутентифицированных пользователей.
"""
    event = await eventservice.get_all_active_events(db=db)
    return event

@router.get("/history", response_model=List[schemas.Event], status_code=status.HTTP_200_OK, summary="Получение прошедших мероприятия")
async def get_old_events(db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):
    """
    Создает новое мероприятие. Доступно только для аутентифицированных пользователей.
"""
    event = await eventservice.get_old_events(db=db)
    return event

@router.get("/{event_id}", response_model=schemas.Event, status_code=status.HTTP_200_OK, summary="Получение мероприятия по ID")
async def get_event_by_id(event_id: int,db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):

    event = await eventservice.get_by_id(db=db,event_id = event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Мероприятие с ID {event_id} не найдено.")
    return event
