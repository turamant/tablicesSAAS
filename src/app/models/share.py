from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func, Enum as SQLEnum
from datetime import datetime
import uuid
from typing import TYPE_CHECKING

from .types import SharePermission

if TYPE_CHECKING:
    from .table import Table
    from .user import User

class TableShare(SQLModel, table=True):
    __tablename__ = "table_shares"
    
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
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", nullable=False)
    permission: SharePermission = Field(
        sa_column=Column(SQLEnum(SharePermission), nullable=False, default=SharePermission.READ)
    )
    
    # Relationships
    table: "Table" = Relationship(back_populates="shares")
    user: "User" = Relationship()