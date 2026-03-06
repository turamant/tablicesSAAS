from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON, DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .table import Table

class View(SQLModel, table=True):
    __tablename__ = "views"
    
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        sa_column_kwargs={"server_default": func.gen_random_uuid()}
    )
    name: str = Field(max_length=255, nullable=False)
    type: str = Field(max_length=50, nullable=False)  # grid, kanban, calendar, gallery
    table_id: uuid.UUID = Field(foreign_key="tables.id", ondelete="CASCADE")
    settings: dict = Field(default={}, sa_column=Column(JSON))
    is_default: bool = Field(default=False)
    created_by: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    )
    
    # Relationships
    table: "Table" = Relationship(back_populates="views")
    user: "User" = Relationship()