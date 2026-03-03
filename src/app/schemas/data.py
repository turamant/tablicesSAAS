from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class DataRecordCreate(BaseModel):
    """Создание записи в динамической таблице"""
    data: Dict[str, Any]  # {field_id: value}
    
    @validator('data')
    def validate_not_empty(cls, v):
        if not v:
            raise ValueError('data cannot be empty')
        return v

class DataRecordUpdate(BaseModel):
    """Обновление записи"""
    data: Dict[str, Any]

class DataRecordResponse(BaseModel):
    """Ответ с записью"""
    id: UUID
    _created_at: datetime
    _created_by: Optional[UUID]
    _updated_at: datetime
    data: Dict[str, Any]  # {field_name: value}

class DataFilter(BaseModel):
    """Фильтр для запросов"""
    field: str
    operator: str = Field(..., pattern='^(eq|ne|gt|lt|gte|lte|like|in)$')
    value: Any

class DataQueryParams(BaseModel):
    """Параметры запроса"""
    filters: Optional[List[DataFilter]] = None
    order_by: Optional[str] = None
    order_direction: str = "asc"
    limit: int = 100
    offset: int = 0