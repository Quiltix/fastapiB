from typing import List

from fastapi import APIRouter, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
from app.service import ticket as ticket_service # <-- Импортируем наш новый сервис
from app.service.security import check_jwt     # <-- Импортируем зависимость для аутентификации

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)

@router.post(
    "/",
    response_model=schemas.Ticket,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация на мероприятие"
)
async def register_user_for_event(
    db: AsyncSession = Depends(get_db),
    schema: schemas.TicketCreate = Body(...),
    user_id: int = Depends(check_jwt), # <-- Аутентификация, получаем ID участника
):
    """
    Регистрирует текущего пользователя на мероприятие по его ID.

    В теле запроса необходимо передать `event_id`.
    """
    ticket = await ticket_service.register_for_event(
        db=db,
        schema=schema,
        participant_id=user_id
    )
    return ticket

@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отмена регистрации на мероприятие"
)
async def cancel_registration_for_event(
    ticket_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(check_jwt), # <-- Аутентификация
):
    """
    Отменяет регистрацию (удаляет билет) на мероприятие по ID билета.

    - Пользователь может отменить только свою регистрацию.
    - Отмена невозможна, если мероприятие уже началось.
    - В случае успеха возвращает пустой ответ со статусом 204.
    """
    await ticket_service.cancel_registration(
        db=db,
        ticket_id=ticket_id,
        user_id=user_id
    )
    # FastAPI автоматически вернет 204 No Content, если эндпоинт ничего не возвращает
    # и у него установлен соответствующий status_code.
    return

@router.get(
    "",
    response_model=List[schemas.Ticket],
    summary="Получение списка моих билетов"
)
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    user_id: int = Depends(check_jwt),
):
    """
    Возвращает список всех мероприятий, на которые зарегистрирован
    текущий пользователь.
    """
    tickets = await ticket_service.get_tickets_by_user_id(db=db, user_id=user_id)
    return tickets