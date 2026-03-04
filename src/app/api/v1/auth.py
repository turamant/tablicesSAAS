
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.api.dependencies import get_current_user_id
from src.app.core.database import get_session
from src.app.schemas.auth import UserLogin, UserRegister, UserResponse
from src.app.services.auth_service import AuthService
from src.app.models.user import User
from src.app.models.refresh_token import RefreshToken


router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(
    user_data: UserRegister,
    response: Response,
    session: AsyncSession = Depends(get_session)
):
    # Проверяем, существует ли пользователь
    from sqlmodel import select
    result = await session.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Создаем пользователя
    user = User(
        email=user_data.email,
        password_hash=AuthService.get_password_hash(user_data.password),
        full_name=user_data.full_name
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    # Создаем токены
    access_token = AuthService.create_access_token({"sub": str(user.id)})
    refresh_token = await AuthService.create_refresh_token_record(session, str(user.id))
    
    # Устанавливаем куки
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True в продакшне с HTTPS
        samesite="lax",
        max_age=900,  # 15 минут
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,  # 7 дней
        path="/"
    )
    
    return {"message": "User created", "user": user.email}

@router.post("/login")
async def login(
    user_data: UserLogin,
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    user = await AuthService.authenticate_user(session, user_data.email, user_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = AuthService.create_access_token({"sub": str(user.id)})
    refresh_token = await AuthService.create_refresh_token_record(
        session, 
        str(user.id),
        request.headers.get("user-agent"),
        request.client.host
    )
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=604800,
        path="/"
    )
    
    return {"message": "Login successful"}

@router.post("/logout")
async def logout(
    response: Response,
    request: Request,
    session: AsyncSession = Depends(get_session)
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await AuthService.revoke_refresh_token(session, refresh_token)
    
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
async def get_me(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)  # <-- Чисто!
):
    user = await session.get(User, user_id)
    return user



@router.post("/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    session: AsyncSession = Depends(get_session)
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")
    
    # Ищем в БД
    result = await session.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.now(timezone.utc)
        )
    )
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Создаем новый access_token
    new_access = AuthService.create_access_token(
        {"sub": str(token_record.user_id)}
    )
    
    response.set_cookie(
        key="access_token",
        value=new_access,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=900,
        path="/"
    )
    
    return {"message": "Token refreshed"}