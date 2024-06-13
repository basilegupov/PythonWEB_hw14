from typing import Optional
from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(body: UserSchema, db: AsyncSession) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: Optional[str],  db: AsyncSession) -> None:
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    # Получаем пользователя по его электронной почте
    user = await get_user_by_email(email, db)
    # Устанавливаем флаг подтверждения у пользователя в True
    user.confirmed = True
    # Коммитим изменения в базе данных
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    # Получаем пользователя по его электронной почте из базы данных
    user = await get_user_by_email(email, db)
    # Обновляем поле avatar пользователя новым URL
    user.avatar = url
    # Сохраняем изменения в базе данных
    await db.commit()
    # Обновляем объект пользователя, чтобы отразить последние изменения
    await db.refresh(user)
    # Возвращаем обновленный объект пользователя
    return user
