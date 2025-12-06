from typing import List

from fastapi import APIRouter, status, Depends, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
from app.service.security import check_jwt
import app.service.event as event_service
import app.service.user as user_service
import app.service.auth as auth_service

router = APIRouter(prefix="/admin",tags=["Admin"])


@router.delete("/events/{event_id}", status_code=status.HTTP_200_OK,
    summary="Удаление мероприятия администратором",
    description="Удаляет мероприятие по его ID. Доступно только для администраторов.")
async def delete_event(event_id: int, db: AsyncSession = Depends(get_db),admin_id = Depends(check_jwt)):
    await event_service.delete_event_by_admin(db=db, event_id=event_id, user_id=admin_id)

@router.delete("/users/{user_id}/ban", response_model=schemas.User,
    summary="Блокировка пользователя администратором",
    description="Блокирует пользователя по его ID. Доступно только для администраторов.")
async def ban_user_by_admin(user_id: int,db: AsyncSession = Depends(get_db), admin_id: int = Depends(check_jwt)):
    banned_user = await user_service.ban_user(db=db,user_id_to_ban=user_id,admin_id = admin_id)
    return banned_user

@router.post("/register", status_code=status.HTTP_200_OK, response_model=schemas.User,
    summary="Регистрация нового администратора",
    description="Регистрирует нового администратора и возвращает его данные.")
async def register(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...), password: str = Query()) -> schemas.User:

    user = await auth_service.register_new_admin(db, schema,password)
    return user

@router.get("/users", status_code=status.HTTP_200_OK,response_model=List[schemas.UserAdminView],
    summary="Получить всех пользователей",
    description="Возвращает всех пользователей")
async def register(db: AsyncSession = Depends(get_db),admin_id: int = Depends(check_jwt)) -> List[schemas.UserAdminView]:
    users = await user_service.get_all_users(db,admin_id)
    return users