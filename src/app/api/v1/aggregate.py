from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.database import get_session
from src.app.models.table import Table
from src.app.schemas.aggregate import AggregateResponse
from src.app.services.aggregate_service import AggregateService
from src.app.api.dependencies import get_current_user_id
from typing import Optional, List
from uuid import UUID

router = APIRouter(prefix="/tables/{table_id}/aggregate", tags=["aggregate"])

@router.get("/", response_model=AggregateResponse)
async def get_aggregations(
    table_id: UUID,
    fields: Optional[str] = Query(None, description="Comma-separated field names"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Получить агрегации для таблицы"""
    # Проверяем доступ к таблице
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
    
    # Парсим список полей
    field_list = None
    if fields:
        field_list = [f.strip() for f in fields.split(',')]
    
    # Получаем агрегации
    aggregations = await AggregateService.get_aggregations(table, field_list)
    
    return aggregations