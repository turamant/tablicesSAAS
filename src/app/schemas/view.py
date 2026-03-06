import enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class ViewType(str, enum.Enum):
    GRID = "grid"
    KANBAN = "kanban"
    CALENDAR = "calendar"
    GALLERY = "gallery"

class ViewSettings(BaseModel):
    """Настройки представления"""
    # Общие настройки
    hidden_fields: List[str] = []  # скрытые поля
    sort_field: Optional[str] = None
    sort_direction: str = "asc"
    filters: List[Dict] = []
    
    # Для Kanban
    kanban_group_field: Optional[str] = None  # поле для группировки (обычно статус)
    kanban_columns: List[str] = []  # колонки (значения поля)

class ViewCreate(BaseModel):
    name: str
    type: ViewType
    table_id: UUID
    settings: ViewSettings
    is_default: bool = False

class ViewResponse(BaseModel):
    id: UUID
    name: str
    type: ViewType
    table_id: UUID
    settings: Dict[str, Any]
    is_default: bool
    created_by: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True