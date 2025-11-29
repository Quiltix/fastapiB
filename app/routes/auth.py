from fastapi import APIRouter, status, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import app.service.user as user_service

from app.db.database import get_db
from app.schemas import schemas

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", status_code=status.HTTP_200_OK, response_model=schemas.User,
    summary="Регистрация нового пользователя",
    description="Регистрирует нового пользователя и возвращает его данные.")
async def register(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...)) -> schemas.User:

    user = await user_service.register_new_user(db, schema)
    return user

@router.post("/login", response_model=schemas.Token,
    summary="Авторизация пользователя",
    description="Авторизирует пользователя и возвращает токен доступа.")
async def login(db: AsyncSession = Depends(get_db), schema: schemas.UserAuth = Body(...)) -> schemas.Token:

    user = await user_service.authenticate_user(db, schema)
    return await user_service.create_user_tokens(user.id)