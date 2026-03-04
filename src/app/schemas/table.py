# table.py
from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from src.app.models.types import FieldType

class FieldCreate(BaseModel):
    name: str
    display_name: str
    field_type: FieldType
    is_required: bool = False
    is_unique: bool = False
    options: Optional[dict] = None
    sort_order: int = 0

class FieldResponse(BaseModel):
    id: UUID
    name: str
    display_name: str
    field_type: FieldType
    is_required: bool
    is_unique: bool
    options: Optional[dict]
    sort_order: int
    
    class Config:
        from_attributes = True

class TableCreate(BaseModel):
    name: str
    description: Optional[str] = None
    fields: List[FieldCreate]


class TableUpdate(BaseModel):
    """Схема для обновления таблицы"""
    name: Optional[str] = None
    description: Optional[str] = None

class TableResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    physical_name: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    fields: List[FieldResponse] = []
    
    class Config:
        from_attributes = True