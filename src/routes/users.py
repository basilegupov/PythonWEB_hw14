"""
Users routes module.

This module defines the endpoints for managing user-related operations.

Routes:
    - /users/me: Endpoint for retrieving the current user's details.
    - /users/avatar: Endpoint for updating the user's avatar.
"""

import pickle

import cloudinary
import cloudinary.uploader
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
)
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserResponse
from src.services.auth import auth_service
from src.conf.config import config
from src.repository import users as repositories_users

router = APIRouter(prefix="/users", tags=["users"])

cloudinary.config(
    cloud_name=config.CLD_NAME,
    api_key=config.CLD_API_KEY,
    api_secret=config.CLD_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    Endpoint for retrieving the current user's details.

    Args:
        user (User): The current authenticated user.

    Returns:
        UserResponse: The current user's details.
    """
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        detail="User successfully created"
    )
    # return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint for updating the user's avatar.

    Args:
        file (UploadFile): The image file for the new avatar.
        user (User): The current authenticated user.
        db (AsyncSession): The asynchronous database session.

    Returns:
        UserResponse: The updated user details with the new avatar.
    """
    public_id = f"Web21/{user.email}"
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    updated_user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)

    return UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        avatar=updated_user.avatar,
        detail="User successfully created"
    )
    # return user
