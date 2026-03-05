from pydantic import BaseModel
from typing import Dict, Optional, Any, List
from uuid import UUID

class AggregateRequest(BaseModel):
    """Запрос на агрегацию"""
    fields: Optional[List[str]] = None  # список полей для агрегации (если None - все числовые)
    include_count: bool = True  # всегда true для первой версии

class AggregateResponse(BaseModel):
    """Ответ с агрегациями"""
    total_records: int
    sums: Dict[str, float] = {}
    averages: Dict[str, float] = {}
    mins: Dict[str, float] = {}
    maxs: Dict[str, float] = {}
    
    class Config:
        from_attributes = True