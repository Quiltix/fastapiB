from rich import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from sqlalchemy.orm import selectinload

from app.db import models
from app.schemas import schemas
from app.service import security


async def register_new_user(db: AsyncSession, user_schema: schemas.UserAuth) -> models.User:

    existing_user = await get_by_username(db, username=user_schema.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь уже существует",
        )


    hashed_password = security.get_password_hash(user_schema.password)

    new_user = await create(db=db, username=user_schema.username, hashed_password=hashed_password)
    return new_user

async def authenticate_user(db: AsyncSession, user_schema: schemas.UserAuth) -> models.User:
    """
    Аутентифицирует пользователя.
    1. Находит пользователя по username.
    2. Проверяет пароль.
    """
    user = await get_by_username(db, username=user_schema.username)

    if not user or not security.verify_password(user_schema.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный логин или пароль",
        )

    return user

async def create_user_tokens(user_id: int) -> schemas.Token:
    """Создает и возвращает access_token для пользователя."""
    access_token = security.create_access_token(data={"sub": str(user_id)})
    return schemas.Token(access_token=access_token, token_type="bearer")

async def get_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    """Получает пользователя по его ID с предзагрузкой связей."""
    query = (
        select(models.User)
        .where(models.User.id == user_id)
        .options(
            selectinload(models.User.created_events),
            selectinload(models.User.tickets)
        )
    )
    result = await db.execute(query)
    return result.scalars().first()

async def get_by_username(db: AsyncSession, username: str) -> models.User | None:
    """Получает пользователя по его имени с предзагрузкой связей."""
    query = (
        select(models.User)
        .where(models.User.username == username)
        .options(
            selectinload(models.User.created_events), # Загрузить созданные мероприятия
            selectinload(models.User.tickets).options(selectinload(models.Ticket.event)) # Загрузить билеты и сразу мероприятия для них
        )
    )
    result = await db.execute(query)
    return result.scalars().first()

async def create(db: AsyncSession, username: str, hashed_password: str) -> models.User:
    """Создает нового пользователя в базе данных."""
    db_user = models.User(username=username, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user




