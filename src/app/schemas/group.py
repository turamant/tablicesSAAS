from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

class GroupByField(BaseModel):
    """Поле для группировки"""
    field: str  # имя поля
    sort_direction: Optional[str] = "asc"  # asc/desc

class AggregateField(BaseModel):
    """Агрегация для поля"""
    field: str  # имя поля
    function: str  # sum, avg, count, min, max
    alias: Optional[str] = None  # псевдоним для результата

class GroupRequest(BaseModel):
    """Запрос на группировку"""
    group_by: List[GroupByField]  # поля для группировки
    aggregates: List[AggregateField]  # агрегации
    filters: Optional[List[Dict]] = None  # фильтры (как в data)
    limit: Optional[int] = 100
    offset: Optional[int] = 0

class GroupResult(BaseModel):
    """Результат группировки"""
    groups: List[Dict[str, Any]]  # сгруппированные данные
    total_groups: int  # всего групп
    grand_totals: Dict[str, Any]  # общие итоги (опционально)