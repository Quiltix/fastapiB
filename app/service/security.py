# app/security.py

import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.schemas.schemas import TokenData

SECRET_KEY = "a_very_secret_key_for_event_platform"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120



def get_password_hash(password: str) -> str:
    # Получение хеша пароля.
    password_bytes = password.encode('utf-8')

    salt = bcrypt.gensalt()
    hashed_password_bytes = bcrypt.hashpw(password_bytes, salt)

    return hashed_password_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Сверяет обычный пароль с захешированным паролем.
    plain_password_bytes = plain_password.encode('utf-8')

    hashed_password_bytes = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    # Создает токен.
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    #Декодирует токен и возвращает данные токена.

    payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

    return TokenData.model_validate(payload)

async def check_jwt(credentials: HTTPBearer = Depends(HTTPBearer(auto_error=False))) -> int:
    # Проверяет токен пользователя, используется в роутерах.
    try:
        if not credentials:
            raise JWTError
        token_data = decode_token(credentials.credentials)
        return int(token_data.sub)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ошибка аутентификации")