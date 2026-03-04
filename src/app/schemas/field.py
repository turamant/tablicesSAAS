from pydantic import BaseModel
from typing import Optional, Any
from uuid import UUID
from datetime import datetime

class FieldCreate(BaseModel):
    name: str
    display_name: str
    field_type: str
    is_required: bool = False
    is_unique: bool = False
    options: Optional[Any] = None
    sort_order: int = 0

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    is_required: Optional[bool] = None

class FieldResponse(BaseModel):
    id: UUID
    table_id: UUID
    name: str
    display_name: str
    field_type: str
    is_required: bool
    is_unique: bool
    options: Optional[Any]
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True