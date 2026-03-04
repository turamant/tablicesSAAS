from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.database import get_session
from src.app.models.table import Table
from src.app.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from src.app.api.dependencies import get_current_user_id
from src.app.services.field_service import FieldService
from typing import List

router = APIRouter(prefix="/tables/{table_id}/fields", tags=["fields"])

@router.post("/", response_model=FieldResponse)
async def create_field(
    table_id: UUID,
    field_data: FieldCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Добавить новое поле в таблицу"""
    table = await FieldService.get_table_and_check_access(table_id, session, user_id)
    return await FieldService.create_field(table, field_data, session)

@router.delete("/{field_id}")
async def delete_field(
    table_id: UUID,
    field_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Удалить поле из таблицы"""
    table = await FieldService.get_table_and_check_access(table_id, session, user_id)
    await FieldService.delete_field(table, field_id, session)
    return {"message": "Field deleted"}

@router.patch("/{field_id}", response_model=FieldResponse)
async def update_field(
    table_id: UUID,
    field_id: UUID,
    field_data: FieldUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Обновить название поля (тип менять нельзя!)"""
    table = await FieldService.get_table_and_check_access(table_id, session, user_id)
    return await FieldService.update_field(table, field_id, field_data, session)

@router.get("/", response_model=List[FieldResponse])
async def get_fields(
    table_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Получить все поля таблицы"""
    table = await FieldService.get_table_and_check_access(table_id, session, user_id)
    return await FieldService.get_fields(table, session)