import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar_url,
)
from src.entity.models import User
from src.schemas.user import UserSchema


@pytest.mark.asyncio
class TestUserRepository:

    async def test_get_user_by_email(self):
        # Mocking the database session
        session = MagicMock(spec=AsyncSession)
        # Test parameters
        email = "test@example.com"
        # Mocking the database query result
        user = User(email=email)
        session.execute = AsyncMock(
            return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=user)))))
        # Calling the function under test
        result = await get_user_by_email(email, session)
        # Verifying the result
        assert result == user

    async def test_create_user(self):
        # Mocking the database session
        session = MagicMock(spec=AsyncSession)
        # Test parameters
        body = UserSchema(email="test@example.com", password="password", username="testuser")
        # Calling the function under test
        result = await create_user(body, session)
        # Verifying that the user is created
        assert isinstance(result, User)
        assert result.email == body.email
        assert result.password == body.password
        assert result.username == body.username

    async def test_update_token(self):
        # Mocking the database session
        session = MagicMock(spec=AsyncSession)
        # Test parameters
        user = User(email="test@example.com")
        token = "new_token"
        # Calling the function under test
        await update_token(user, token, session)
        # Verifying that the user's token is updated
        assert user.refresh_token == token

    async def test_confirmed_email(self):
        # Mocking the database session
        session = MagicMock(spec=AsyncSession)
        # Test parameters
        email = "test@example.com"
        # Mocking the database query result
        user = User(email=email)
        session.execute = AsyncMock(
            return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=user)))))
        # Calling the function under test
        await confirmed_email(email, session)
        # Verifying that the user's email is confirmed
        assert user.confirmed

    async def test_update_avatar_url(self):
        # Mocking the database session
        session = MagicMock(spec=AsyncSession)
        # Test parameters
        email = "test@example.com"
        url = "http://example.com/avatar.jpg"
        # Mocking the database query result
        user = User(email=email)
        session.execute = AsyncMock(
            return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=user)))))
        # Calling the function under test
        result = await update_avatar_url(email, url, session)
        # Verifying that the user's avatar URL is updated
        assert result.avatar == url
