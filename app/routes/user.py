from typing import List

from fastapi import APIRouter, status, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
import app.service.user as user_service
import app.service.event as event_service
from app.service.security import check_jwt

router = APIRouter(prefix="/user", tags=["User"])

@router.post("/register", status_code=status.HTTP_200_OK, response_model=schemas.User, summary="Регистрация нового пользователя")
async def register(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...)) -> schemas.User:
    """Регистрирует нового пользователя.

    Принимает на вход данные пользователя (username и password) и возвращает созданного пользователя.
    """
    user = await user_service.register_new_user(db, schema)
    return user

@router.post("/login", response_model=schemas.Token,
    summary="Авторизация пользователя",
    description="Авторизирует пользователя и возвращает токен доступа.")
async def login(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...)) -> schemas.Token:
    user = await user_service.authenticate_user(db, schema)
    return await user_service.create_user_tokens(user.id)

@router.patch("/username", response_model=schemas.User,
    summary="Сменить имя пользователя",
    description="Обновляет имя пользователя.")
async def update_user_username(db: AsyncSession = Depends(get_db), schema: schemas.UpdateUsername = Body(...), user_id: int = Depends(check_jwt),):
    current_user = await user_service.get_by_id(db, user_id)
    updated_user = await user_service.update_username(db=db, current_user=current_user, new_username=schema.username)
    return updated_user

@router.patch("/password", status_code=status.HTTP_200_OK,
    summary="Сменить пароль",
    description="Обновляет пароль пользователя.")
async def update_user_password(db: AsyncSession = Depends(get_db), schema: schemas.UpdatePassword = Body(...), user_id: int = Depends(check_jwt),):
    current_user = await user_service.get_by_id(db, user_id)
    await user_service.update_password(db=db, current_user=current_user, old_password=schema.old_password, new_password=schema.new_password)
    return None

@router.get("/events", response_model=List[schemas.EventShort],
    summary="Получение списка мероприятий, созданных пользователем",
    description="Возвращает список мероприятий, которые создал пользователь")
async def get_my_created_events(db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):
    events = await event_service.get_events_by_owner(db=db, owner_id=user_id)
    return events

@router.get("/events/active", response_model=List[schemas.EventShort],
    summary="Получение списка будущих мероприятий, созданных пользователем",
    description="Возвращает список мероприятий, которые создал пользователь и они не прошли")
async def get_my_created_events_active(db: AsyncSession = Depends(get_db), user_id: int = Depends(check_jwt)):
    events = await event_service.get_events_by_owner_active(db=db, owner_id=user_id)
    return events