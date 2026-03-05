from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.database import get_session
from src.app.models.table import Table
from src.app.services.export_service import ExportService
from src.app.services.data_service import DataService
from src.app.services.aggregate_service import AggregateService
from src.app.api.dependencies import get_current_user_id
from src.app.schemas.data import DataQueryParams
from uuid import UUID

router = APIRouter(prefix="/tables/{table_id}/export", tags=["export"])

@router.get("/excel")
async def export_to_excel(
    table_id: UUID,
    include_aggregations: bool = Query(False, description="Включить итоги"),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Экспорт таблицы в Excel"""
    # Проверяем доступ
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
    
    # Получаем все записи
    params = DataQueryParams(limit=10000)  # ограничение на 10к записей
    records = await DataService.get_records(table, user_id, params)
    
    # Получаем агрегации если нужно
    aggregations = None
    if include_aggregations:
        aggregations = await AggregateService.get_aggregations(table)
    
    # Экспортируем
    return await ExportService.export_to_excel(table, records, include_aggregations, aggregations)