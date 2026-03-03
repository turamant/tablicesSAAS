from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt
from passlib.context import CryptContext
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from src.app.models.user import User
from src.app.models.refresh_token import RefreshToken
from src.app.core.config import settings
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля через bcrypt"""
        try:
            plain_bytes = plain_password.encode('utf-8')[:72]
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширование пароля через bcrypt"""
        # Принудительно обрезаем до 72 байт и кодируем
        password_bytes = password.encode('utf-8')[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token() -> str:
        return str(uuid.uuid4())

    @classmethod
    async def authenticate_user(cls, session: AsyncSession, email: str, password: str) -> User | None:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user or not cls.verify_password(password, user.password_hash):
            return None
        return user

    @classmethod
    async def create_refresh_token_record(cls, session: AsyncSession, user_id: str, user_agent: str = None, ip: str = None) -> str:
        token = cls.create_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip
        )
        session.add(refresh_token)
        await session.commit()
        return token

    @classmethod
    async def revoke_refresh_token(cls, session: AsyncSession, token: str):
        result = await session.execute(select(RefreshToken).where(RefreshToken.token == token))
        refresh_token = result.scalar_one_or_none()
        if refresh_token:
            refresh_token.is_revoked = True
            await session.commit()