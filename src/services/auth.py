import pickle

from typing import Optional
from jose import JWTError, jwt

import redis

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repository_users
from src.conf.config import config


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    cache = redis.Redis(
        host=config.REDIS_DOMAIN,
        port=config.REDIS_PORT,
        db=0,
        password=config.REDIS_PASSWORD,
    )

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        return self.pwd_context.hash(password)

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.now(timezone.utc), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user_hash = str(email)

        user = self.cache.get(user_hash)

        if user is None:
            print("User from database")
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.cache.set(user_hash, pickle.dumps(user))
            self.cache.expire(user_hash, 300)
        else:
            print("User from cache")
            user = pickle.loads(user)
        return user

    def create_email_token(self, data: dict):
        """
        Создает JWT-токен для подтверждения email.
        Args:data (dict): Данные для кодирования в токене.
        Returns: str: Сгенерированный JWT-токен.
        """
        to_encode = data.copy()  # Создаем копию данных
        expire = datetime.utcnow() + timedelta(days=1)  # Устанавливаем срок действия токена на 1 день
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})  # Добавляем дату создания и срок действия токена
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)  # Кодируем данные в токен
        return token

    async def get_email_from_token(self, token: str):
        """
        Извлекает email из JWT-токена.
        Args: token (str): JWT-токен.
        Returns: str: Email, извлеченный из токена.
        Raises: HTTPException: Если токен недействителен.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])  # Декодируем токен
            email = payload["sub"]  # Получаем email из полезной нагрузки токена
            return email
        except JWTError as e:
            print(e)  # Выводим сообщение об ошибке
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")  # Вызываем исключение, если токен недействителен




auth_service = Auth()
