from fastapi import APIRouter, status, HTTPException, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas import schemas
import app.service.user as userservice

router = APIRouter(
    prefix="/user"
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