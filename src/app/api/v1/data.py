from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.database import get_session
from src.app.models.table import Table
from src.app.api.dependencies import get_current_user_id
from src.app.schemas.data import DataRecordCreate, DataRecordUpdate, DataQueryParams, DataFilter
from src.app.services.data_service import DataService
from typing import List, Optional
from uuid import UUID
import json

router = APIRouter(prefix="/tables/{table_id}/data", tags=["data"])

async def get_table_and_check_access(
    table_id: UUID,
    session: AsyncSession,
    user_id: str
) -> Table:
    """Хелпер для получения таблицы и проверки доступа"""
    result = await session.execute(
        select(Table)
        .where(Table.id == table_id)
        .options(selectinload(Table.fields))
    )
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if str(table.owner_id) != user_id:  # <-- ИСПРАВЛЕНО: сравниваем строки
        print(f"Owner ID: {table.owner_id}, User ID: {user_id}")
        raise HTTPException(status_code=403, detail="Access denied")
    
    return table

@router.post("/")
async def create_record(
    table_id: UUID,  # <-- FastAPI сам сконвертит строку в UUID
    record: DataRecordCreate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Создать запись в таблице"""
    table = await get_table_and_check_access(table_id, session, user_id)
    
    try:
        result = await DataService.create_record(table, user_id, record.data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
async def list_records(
    table_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id),
    filters: Optional[str] = Query(None, description="JSON array of filters"),
    order_by: Optional[str] = None,
    order_direction: str = "asc",
    limit: int = 100,
    offset: int = 0
):
    """Получить список записей с фильтрацией"""
    table = await get_table_and_check_access(table_id, session, user_id)
    
    # Парсим фильтры из JSON
    filter_objects = []
    if filters:
        try:
            filter_data = json.loads(filters)
            for f in filter_data:
                filter_objects.append(DataFilter(**f))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid filters: {e}")
    
    params = DataQueryParams(
        filters=filter_objects or None,
        order_by=order_by,
        order_direction=order_direction,
        limit=min(limit, 1000),
        offset=offset
    )
    
    records = await DataService.get_records(table, user_id, params)
    return records

@router.get("/{record_id}")
async def get_record(
    table_id: UUID,
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Получить одну запись"""
    table = await get_table_and_check_access(table_id, session, user_id)
    
    params = DataQueryParams(
        filters=[DataFilter(field="id", operator="eq", value=str(record_id))],
        limit=1
    )
    
    records = await DataService.get_records(table, user_id, params)
    if not records:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return records[0]

@router.put("/{record_id}")
async def update_record(
    table_id: UUID,
    record_id: UUID,
    record: DataRecordUpdate,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Обновить запись"""
    table = await get_table_and_check_access(table_id, session, user_id)
    
    try:
        result = await DataService.update_record(table, record_id, user_id, record.data)
        if not result:
            raise HTTPException(status_code=404, detail="Record not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{record_id}")
async def delete_record(
    table_id: UUID,
    record_id: UUID,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Удалить запись"""
    table = await get_table_and_check_access(table_id, session, user_id)
    
    deleted = await DataService.delete_record(table, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {"message": "Record deleted"}