"""
Authentication routes module.

This module defines the authentication endpoints for user registration, login, token refresh,
email confirmation, and email request.

Routes:
    - /auth/signup: Endpoint for user registration.
    - /auth/login: Endpoint for user login.
    - /auth/refresh_token: Endpoint for refreshing access tokens.
    - /auth/confirmed_email/{token}: Endpoint for confirming email addresses.
    - /auth/request_email: Endpoint for requesting email confirmation.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.database.db import get_db
from src.schemas.user import UserSchema, UserResponse, TokenSchema, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user registration.

    Args:
        body (UserSchema): The user data to register.
        bt (BackgroundTasks): Background task to send email confirmation.
        request (Request): The request object.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing user details and registration confirmation message.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST)

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Endpoint for user login.

    Args:
        body (OAuth2PasswordRequestForm): The login form data.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing access token, refresh token, and token type.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_EMAIL)
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.EMAIL_NOT_CONFIRMED)
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD)
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    """
    Endpoint for refreshing access tokens.

    Args:
        credentials (HTTPAuthorizationCredentials): The authorization credentials containing the refresh token.
        db (Session): The database session.

    Returns:
        dict: A dictionary containing new access token, refresh token, and token type.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for confirming email addresses.

    Args:
        token (str): The email confirmation token.
        db (AsyncSession): The asynchronous database session.

    Returns:
        dict: A dictionary containing a confirmation message.
    """
    email = await auth_service.get_email_from_token(token)  # Получаем email из токена
    user = await repository_users.get_user_by_email(email, db)  # Получаем пользователя по email из базы данных
    if user is None:  # Если пользователь не найден
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR)
    if user.confirmed:  # Если email уже подтвержден
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)  # Подтверждаем email
    return {"message": "Email confirmed"}  # Возвращаем сообщение об успешном подтверждении email


# Этот код представляет собой обработчик POST-запроса для запроса подтверждения email.
@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Endpoint for requesting email confirmation.

    Args:
        body (RequestEmail): The email request data.
        background_tasks (BackgroundTasks): Background task to send email confirmation.
        request (Request): The request object.
        db (AsyncSession): The asynchronous database session.

    Returns:
        dict: A dictionary containing a confirmation message.
    """
    user = await repository_users.get_user_by_email(body.email, db)  # Получаем пользователя по email из базы данных

    if user.confirmed:  # Если email уже подтвержден
        return {"message": "Your email is already confirmed"}
    if user:  # Если пользователь существует
        background_tasks.add_task(send_email, user.email, user.username,
                                  str(request.base_url))  # Добавляем задачу отправки email
    return {"message": "Check your email for confirmation."}  # Возвращаем сообщение о запросе подтверждения email


# Этот код представляет собой обработчик GET-запроса для отслеживания того, что пользователь открыл email.
@router.get('/{username}')
async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_db)):
    """
    Endpoint for handling email opening tracking.

    Args:
        username (str): The username for tracking.
        response (Response): The response object.
        db (AsyncSession): The asynchronous database session.

    Returns:
        FileResponse: The image file response.
    """
    print('--------------------------------')
    print(f'{username} зберігаємо що він відкрив email в БД')
    print('--------------------------------')
    return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")
