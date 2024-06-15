"""
Repository module for user operations.

This module contains functions for interacting with the user database table.

Functions:
    get_user_by_email: Retrieves a user by email address.
    create_user: Creates a new user.
    update_token: Updates the refresh token for a user.
    confirmed_email: Confirms the email address for a user.
    update_avatar_url: Updates the avatar URL for a user.
"""

from typing import Optional
from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    """
    Retrieves a user by email address asynchronously.

    Args:
        email (str): The email address of the user.
        db (AsyncSession): The asynchronous database session.

    Returns:
        Optional[User]: The user object if found, otherwise None.
    """
    result = await db.execute(select(User).filter(User.email == email))
    return result.scalars().first()


async def create_user(body: UserSchema, db: AsyncSession) -> User:
    """
    Creates a new user.

    Args:
        body (UserModel): The user data to create.
        db (Session): The database session.

    Returns:
        User: The created user object.
    """
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
    """
    Updates the refresh token for a user.

    Args:
        user (User): The user object to update.
        token (str): The new refresh token.
        db (Session): The database session.
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    Confirms the email address for a user.

    Args:
        email (str): The email address to confirm.
        db (AsyncSession): The asynchronous database session.
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
    Updates the avatar URL for a user.

    Args:
        email (str): The email address of the user.
        url (str | None): The new avatar URL.
        db (AsyncSession): The asynchronous database session.

    Returns:
        User: The updated user object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user
