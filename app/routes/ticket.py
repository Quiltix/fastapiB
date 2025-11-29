from typing import List

from fastapi import APIRouter, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
from app.service import ticket as ticket_service # <-- Импортируем наш новый сервис
from app.service.security import check_jwt     # <-- Импортируем зависимость для аутентификации

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("/", response_model=schemas.Ticket, status_code=status.HTTP_201_CREATED,
    summary="Регистрация на мероприятие",
    description="Позволяет зарегистрировать текущего пользователя на мероприятие. Нельзя зарегистрироваться дважды на одно мероприятие.")
async def register_user_for_event(db: AsyncSession = Depends(get_db), schema: schemas.TicketCreate = Body(...), user_id: int = Depends(check_jwt)):
    ticket = await ticket_service.register_for_event(db=db, schema=schema, participant_id=user_id)
    return ticket

@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена регистрации на мероприятие",
    description="Позволяет отменить регистрацию текущего пользователя на зарегистрированное мероприятие. Нельзя отменить регистрацию, если мероприятие уже началось.")
async def cancel_registration_for_event(ticket_id: int, db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):
    await ticket_service.cancel_registration(db=db, ticket_id=ticket_id, user_id=user_id)
    return

@router.get("", response_model=List[schemas.Ticket],
    summary="Получение моих билетов",
    description="Возвращает список всех билетов, на которые подтвердил пользователь.")
async def get_my_tickets(db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt),):
    tickets = await ticket_service.get_tickets_by_user_id(db=db, user_id=user_id)
    return tickets