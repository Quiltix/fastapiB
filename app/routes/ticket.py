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