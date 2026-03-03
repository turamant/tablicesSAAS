from fastapi import Request, HTTPException, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.database import get_session

async def get_current_user_id(request: Request) -> str:
    user_id = request.state.user_id
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user_id

async def get_current_user_id_optional(request: Request) -> str | None:
    return request.state.user_id