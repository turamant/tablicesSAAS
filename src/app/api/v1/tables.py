from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.database import get_session
from src.app.schemas.table import TableCreate, TableResponse
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
    table_id: str,
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
    
    if table.owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    return table