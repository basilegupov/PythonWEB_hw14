"""
Configuration module for the application.

This module defines the settings using Pydantic's BaseSettings.

Attributes:
    DB_URL (str): The URL for the database connection.
    SECRET_KEY_JWT (str): The secret key for JWT token generation.
    ALGORITHM (str): The algorithm used for JWT token encoding.
    MAIL_USERNAME (EmailStr): The email address for SMTP authentication.
    MAIL_PASSWORD (str): The password for SMTP authentication.
    MAIL_FROM (str): The sender email address for outgoing emails.
    MAIL_PORT (int): The port number for the SMTP server.
    MAIL_SERVER (str): The SMTP server address.
    REDIS_DOMAIN (str): The domain of the Redis server.
    REDIS_PORT (int): The port of the Redis server.
    REDIS_PASSWORD (str): The password for the Redis server, optional.
    CLD_NAME (str): The name of the cloud service.
    CLD_API_KEY (int): The API key for the cloud service.
    CLD_API_SECRET (str): The API secret for the cloud service.

"""
from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:111111@localhost:5432/abc"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "postgres@meail.com"
    MAIL_PASSWORD: str = "postgres"
    MAIL_FROM: str = "postgres"
    MAIL_PORT: int = 567234
    MAIL_SERVER: str = "postgres"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = 'abc'
    CLD_API_KEY: int = 326488457974591
    CLD_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any):
        if v not in ["HS256", "HS512"]:
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra='ignore', env_file=".env", env_file_encoding="utf-8")  # noqa


config = Settings()
