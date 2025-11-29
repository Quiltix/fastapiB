from typing import List

from fastapi import APIRouter, status, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
import app.service.user as userservice
import app.service.event as eventservice
from app.service.security import decode_token, check_jwt

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

@router.post("/register", status_code=status.HTTP_200_OK, response_model=schemas.User, summary="Регистрация нового пользователя")
async def register(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...)) -> schemas.User:
    """Регистрирует нового пользователя.

    Принимает на вход данные пользователя (username и password) и возвращает созданного пользователя.
    """
    user = await userservice.register_new_user(db, schema)
    return user

@router.post("/login", response_model=schemas.Token,summary="Авторизация пользователя")
async def login(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...)) -> schemas.Token:
    """Авторизирует пользователя

    Принимает на вход данные пользователя (username и password) и возвращает токен доступа."""
    user = await userservice.authenticate_user(db, schema)
    return await userservice.create_user_tokens(user.id)

@router.patch("/username", response_model=schemas.User, summary="Сменить имя пользователя")
async def update_user_username(db: AsyncSession = Depends(get_db), schema: schemas.UpdateUsername = Body(...), user_id: int = Depends(check_jwt),):
    """
    Обновляет имя текущего пользователя.
    """
    current_user = await userservice.get_by_id(db, user_id)
    updated_user = await userservice.update_username(db=db, current_user=current_user, new_username=schema.username)
    return updated_user

@router.patch("/me/password", status_code=status.HTTP_200_OK, summary="Сменить пароль")
async def update_user_password(db: AsyncSession = Depends(get_db), schema: schemas.UpdatePassword = Body(...), user_id: int = Depends(check_jwt),):
    """
    Обновляет пароль текущего пользователя.
    При успешной смене пароля возвращает пустой ответ со статусом 204.
    """
    current_user = await userservice.get_by_id(db, user_id)
    await userservice.update_password(db=db, current_user=current_user, old_password=schema.old_password, new_password=schema.new_password
    )
    return None

@router.get("/events", response_model=List[schemas.EventShort], summary="Получение списка мероприятий, созданных пользователем")
async def get_my_created_events(db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):

    events = await eventservice.get_events_by_owner(db=db, owner_id=user_id)
    return events