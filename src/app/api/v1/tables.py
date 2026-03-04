from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from sqlalchemy import text
from src.app.core.database import get_session, engine  # ← engine нужен!
from src.app.schemas.table import TableCreate, TableResponse, TableUpdate  # ← импорт схемы!
from src.app.services.table_service import TableService
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.api.dependencies import get_current_user_id
from typing import List

router = APIRouter(prefix="/tables", tags=["tables"])

@router.post("/", response_model=TableResponse)
async def create_table(
    table_data: TableCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    table = await TableService.create_table(session, user_id, table_data)
    
    await session.refresh(table, {"fields"})
    return table

@router.get("/", response_model=List[TableResponse])
async def list_tables(
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    result = await session.execute(
        select(Table)
        .where(Table.owner_id == user_id)
        .options(selectinload(Table.fields))
    )
    tables = result.scalars().all()
    return tables


@router.get("/{table_id}", response_model=TableResponse)
async def get_table(
    table_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    result = await session.execute(
        select(Table)
        .where(Table.id == table_id)
        .options(selectinload(Table.fields))
    )
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if str(table.owner_id) != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    return table


@router.delete("/{table_id}")
async def delete_table(
    table_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Удалить таблицу"""
    result = await session.execute(
        select(Table).where(Table.id == table_id)
    )
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if str(table.owner_id) != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    # ПРОФЕССИОНАЛЬНО: через сервис, а не в контроллере!
    await TableService.delete_table(session, table)
    
    return {"message": "Table deleted"}


@router.patch("/{table_id}", response_model=TableResponse)
async def update_table(
    table_id: UUID,
    table_data: TableUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Обновить название/описание таблицы"""
    # Загружаем таблицу С ПОЛЯМИ сразу!
    result = await session.execute(
        select(Table)
        .where(Table.id == table_id)
        .options(selectinload(Table.fields))  # ← ЭТО ВАЖНО!
    )
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if str(table.owner_id) != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    # Обновляем только переданные поля
    if table_data.name is not None:
        table.name = table_data.name
    if table_data.description is not None:
        table.description = table_data.description
    
    await session.commit()
    await session.refresh(table)
    
    return table