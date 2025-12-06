from rich import status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException
from sqlalchemy.orm import selectinload, joinedload

from app.db import models
from app.schemas import schemas
from app.service import security

async def update_username(db: AsyncSession, current_user: models.User, new_username: str) -> models.User:
    # Обновление имени пользователя
    existing_user = await get_by_username(db, username=new_username)
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Это имя пользователя уже занято.")

    current_user.username = new_username

    updated_user = await update(db, user=current_user)
    return updated_user


async def update_password(db: AsyncSession, current_user: models.User, old_password: str, new_password: str) -> models.User:
    if not security.verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный текущий пароль.")

    new_hashed_password = security.get_password_hash(new_password)

    current_user.hashed_password = new_hashed_password

    updated_user = await update(db, user=current_user)
    return updated_user


async def get_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    # Получение пользователя по ID с созданными событиями и билетами
    query = (
        select(models.User)
        .where(models.User.id == user_id)
        .options(
            joinedload(models.User.created_events),
            joinedload(models.User.tickets)
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().first()

async def get_by_username(db: AsyncSession, username: str) -> models.User | None:
    # Получение пользователя по имени с созданными событиями и билетами
    query = (
        select(models.User)
        .where(models.User.username == username)
        .options(
            joinedload(models.User.created_events),
            joinedload(models.User.tickets).options(joinedload(models.Ticket.event))
        )
    )
    result = await db.execute(query)
    return result.scalars().unique().first()

async def update(db: AsyncSession, user: models.User) -> models.User:
    # Обновление пользователя
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def ban_user(db: AsyncSession, user_id_to_ban: int, admin_user_id: int) -> models.User:
    # Блокирует пользователя (только для администраторов).
    admin_user = await get_by_id(db, user_id=admin_user_id)
    if user_id_to_ban == admin_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Администратор не может заблокировать сам себя.")

    user_to_ban = await get_by_id(db, user_id=user_id_to_ban)
    if not user_to_ban:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь для блокировки не найден.")

    user_to_ban.banned = True
    user_to_ban.user = "Banned_"+ user_to_ban.id
    await update(db, user=user_to_ban)
    return user_to_ban




