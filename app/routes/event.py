# app/routers/events.py
from typing import List

from fastapi import APIRouter, status, Depends, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
from app.service import event as event_service
from app.service.security import check_jwt

router = APIRouter(prefix="/events", tags=["Events"])

@router.post("", response_model=schemas.Event, status_code=status.HTTP_200_OK,
    summary="Создание нового мероприятия",
    description="Создает новое мероприятие и возвращает его ID. Доступно только для аутентифицированных пользователей.")
async def create_new_event(db: AsyncSession = Depends(get_db), schema: schemas.EventCreate = Body(...),user_id: int = Depends(check_jwt)):

    event = await event_service.create_event(db=db, schema=schema, user_id=user_id)
    return event

@router.patch("/{event_id}", response_model=schemas.Event,
    summary="Редактирование мероприятия",
    description="Редактирование мероприятия только для владельца мероприятия. Позволяет изменять данные частично, без необходимости указывать все поля")
async def update_event(event_id: int, db: AsyncSession = Depends(get_db), schema: schemas.EventUpdate = Body(...), user_id: int = Depends(check_jwt),):

    updated_event = await event_service.update_event(db=db, event_id=event_id, schema=schema, user_id=user_id)
    return updated_event

@router.get("/active", response_model=List[schemas.EventShort], status_code=status.HTTP_200_OK,
    summary="Получение будущих мероприятий",
    description="Получение списка всех будущих мероприятий.")
async def get_active_events(db: AsyncSession = Depends(get_db),user_id: int = Depends(check_jwt)):

    event = await event_service.get_all_active_events(db=db)
    return event

@router.get("/history", response_model=List[schemas.EventShort], status_code=status.HTTP_200_OK,
    summary="Получение прошедших мероприятия",
    description="Получение списка всех прошедших мероприятий(Дата начала уже прошла).")
async def get_old_events(db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):

    event = await event_service.get_old_events(db=db)
    return event

@router.get("/{event_id}", response_model=schemas.Event, status_code=status.HTTP_200_OK,
    summary="Получение мероприятия по ID",
    description="Получение мероприятия по ID. Возвращает полную информацию о мероприятии.")
async def get_event_by_id(event_id: int,db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):

    event = await event_service.get_by_id(db=db,event_id = event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Мероприятие с ID {event_id} не найдено.")
    return event
