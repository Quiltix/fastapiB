from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
from app.service.security import check_jwt
import app.service.event as event_service
import app.service.user as user_service

router = APIRouter(prefix="/admin",tags=["Admin"])


@router.delete("/events/{event_id}", status_code=status.HTTP_200_OK,
    summary="Удаление мероприятия администратором",
    description="Удаляет мероприятие по его ID. Доступно только для администраторов.")
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db),admin_id = Depends(check_jwt)):
    await event_service.delete_event_by_admin(db=db, event_id=event_id, user_id=admin_id)

@router.post("/users/{user_id}/ban", response_model=schemas.User,
    summary="Блокировка пользователя администратором",
    description="Блокирует пользователя по его ID. Доступно только для администраторов.")
async def ban_user_by_admin(user_id: int,db: AsyncSession = Depends(get_db), admin_id: int = Depends(check_jwt)):
    banned_user = await user_service.ban_user(db=db,user_id_to_ban=user_id,admin_user_id = admin_id)
    return banned_user