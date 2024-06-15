"""
Schemas module.

This module contains Pydantic models for representing data structures used in the application.

Models:
    - UserSchema: Schema for user.
    - UserResponse: Schema for representing a user response.
    - TokenModel: Schema for representing an access token and a refresh token.
    - RequestEmail: Schema for representing a request email.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserSchema(BaseModel):
    """Schema for user."""
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6, max_length=8)


class UserResponse(BaseModel):
    """Schema for representing a user response."""
    id: int = 1
    username: str
    email: EmailStr
    avatar: str
    model_config = ConfigDict(from_attributes = True)


class TokenSchema(BaseModel):
    """Schema for representing an access token and a refresh token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """Schema for representing a request email."""
    email: EmailStr
