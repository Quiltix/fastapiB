from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import models
from app.schemas import schemas
import app.service.user as user_service
from app.service import security

async def register_new_user(db: AsyncSession, user_schema: schemas.UserAuth) -> models.User:
    # Регистрация нового пользователя
    existing_user = await user_service.get_by_username(db, username=user_schema.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь уже существует")

    hashed_password = security.get_password_hash(user_schema.password)

    new_user_instance = await create(db=db, username=user_schema.username, hashed_password=hashed_password)

    created_user = await user_service.get_by_id(db, user_id=new_user_instance.id)

    return created_user

async def authenticate_user(db: AsyncSession, user_schema: schemas.UserAuth) -> models.User:
    # Аутентификация пользователя
    user = await user_service.get_by_username(db, username=user_schema.username)

    if not user or not security.verify_password(user_schema.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный логин или пароль")

    return user

async def create(db: AsyncSession, username: str, hashed_password: str) -> models.User:
    # Создание нового пользователя
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user