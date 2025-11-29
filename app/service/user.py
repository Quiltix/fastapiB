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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже существует",
        )


    hashed_password = security.get_password_hash(user_schema.password)

    new_user_instance = await create(
        db=db,
        username=user_schema.username,
        hashed_password=hashed_password
    )

    created_user = await get_by_id(db, user_id=new_user_instance.id)

    return created_user

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

async def update_username(db: AsyncSession, current_user: models.User, new_username: str) -> models.User:

    existing_user = await get_by_username(db, username=new_username)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Это имя пользователя уже занято."
        )

    current_user.username = new_username

    updated_user = await update(db, user=current_user)
    return updated_user


async def update_password(db: AsyncSession, current_user: models.User, old_password: str, new_password: str) -> models.User:
    if not security.verify_password(old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный текущий пароль."
        )

    new_hashed_password = security.get_password_hash(new_password)

    current_user.hashed_password = new_hashed_password

    updated_user = await update(db, user=current_user)
    return updated_user

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
            selectinload(models.User.created_events),
            selectinload(models.User.tickets).options(selectinload(models.Ticket.event))
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

async def update(db: AsyncSession, user: models.User) -> models.User:
    """Сохраняет изменения в объекте пользователя в БД."""
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user




