from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from sqlalchemy import DateTime, func, Enum as SQLEnum
from datetime import datetime
import uuid
from typing import Optional, TYPE_CHECKING

from .types import FieldType

if TYPE_CHECKING:
    from .table import Table

class Field(SQLModel, table=True):
    __tablename__ = "fields"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": func.gen_random_uuid()}
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    )
    
    table_id: uuid.UUID = Field(foreign_key="tables.id", ondelete="CASCADE", nullable=False)
    name: str = Field(max_length=255, nullable=False)
    display_name: str = Field(max_length=255, nullable=False)
    field_type: FieldType = Field(
        sa_column=Column(SQLEnum(FieldType), nullable=False)
    )
    is_required: bool = Field(default=False)
    is_unique: bool = Field(default=False)
    options: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    sort_order: int = Field(default=0)
    
    # Relationships
    table: "Table" = Relationship(back_populates="fields")