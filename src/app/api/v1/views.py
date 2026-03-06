from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.database import get_session
from src.app.schemas.view import ViewCreate, ViewResponse
from src.app.services.view_service import ViewService
from src.app.api.dependencies import get_current_user_id
from uuid import UUID
from typing import List

router = APIRouter(prefix="/tables/{table_id}/views", tags=["views"])

@router.post("/", response_model=ViewResponse)
async def create_view(
    table_id: UUID,
    view_data: ViewCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    return await ViewService.create_view(table_id, view_data, session, user_id)

@router.get("/", response_model=List[ViewResponse])
async def list_views(
    table_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    return await ViewService.get_views(table_id, session, user_id)

@router.get("/{view_id}", response_model=ViewResponse)
async def get_view(
    table_id: UUID,
    view_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    return await ViewService.get_view(table_id, view_id, session, user_id)

@router.put("/{view_id}", response_model=ViewResponse)
async def update_view(
    table_id: UUID,
    view_id: UUID,
    view_data: ViewCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    return await ViewService.update_view(table_id, view_id, view_data, session, user_id)

@router.delete("/{view_id}")
async def delete_view(
    table_id: UUID,
    view_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    await ViewService.delete_view(table_id, view_id, session, user_id)
    return {"message": "View deleted"}