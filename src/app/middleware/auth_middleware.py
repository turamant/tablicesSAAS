from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError
from src.app.core.config import settings

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print(f"\n=== AUTH MIDDLEWARE ===")
        print(f"Path: {request.url.path}")
        print(f"All cookies: {request.cookies}")
        
        # Точное совпадение путей, а не startswith!
        public_paths = [
            "/", 
            "/docs", 
            "/openapi.json",
            "/auth/login",
            "/auth/register"
        ]
        
        if request.url.path in public_paths:
            print("Public path - skipping auth")
            return await call_next(request)
        
        access_token = request.cookies.get("access_token")
        print(f"Access token from cookie: {access_token}")
        
        if not access_token:
            print("No access token")
            request.state.user_id = None
            return await call_next(request)
        
        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            print(f"Decoded user_id: {user_id}")
            request.state.user_id = user_id
        except JWTError as e:
            print(f"JWT Error: {e}")
            request.state.user_id = None
        
        return await call_next(request)