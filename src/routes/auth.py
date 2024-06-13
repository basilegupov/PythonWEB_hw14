from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request, Response
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas.user import UserSchema, UserResponse, TokenSchema, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.email import send_email

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    bt.add_task(send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post("/login", response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security),
                        db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Обработчик маршрута для подтверждения email по токену.
    Args:
        token (str): JWT-токен для подтверждения email.
        db (AsyncSession): Сессия базы данных.
    Returns:
        dict: Сообщение об успешном подтверждении email.
    Raises:
        HTTPException: Если произошла ошибка при подтверждении email.
    """
    email = await auth_service.get_email_from_token(token)  # Получаем email из токена
    user = await repository_users.get_user_by_email(email, db)  # Получаем пользователя по email из базы данных
    if user is None:  # Если пользователь не найден
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:  # Если email уже подтвержден
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)  # Подтверждаем email
    return {"message": "Email confirmed"}  # Возвращаем сообщение об успешном подтверждении email


# Этот код представляет собой обработчик POST-запроса для запроса подтверждения email.
@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    Обработчик POST-запроса для запроса подтверждения email.
    Args:
        body (RequestEmail): Тело запроса, содержащее email.
        background_tasks (BackgroundTasks): Фоновые задачи FastAPI.
        request (Request): Запрос FastAPI.
        db (AsyncSession): Сессия базы данных.
    Returns: dict: Сообщение о запросе подтверждения email.

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
    Обработчик GET-запроса для отслеживания того, что пользователь открыл email.
    Args:
        username (str): Имя пользователя, для которого происходит отслеживание.
        response (Response): Ответ FastAPI.
        db (AsyncSession): Сессия базы данных.
    Returns:
        FileResponse: Файл изображения для отображения в браузере.
    """
    print('--------------------------------')
    print(f'{username} зберігаємо що він відкрив email в БД')
    print('--------------------------------')
    return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")