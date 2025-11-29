# app/routers/events.py

from fastapi import APIRouter, status, Depends, Body
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