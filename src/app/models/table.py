from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
import uuid
from typing import List, TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .user import User
    from .field import Field
    from .share import TableShare
    from .view import View

class Table(SQLModel, table=True):
    __tablename__ = "tables"
    
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
    
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    physical_name: str = Field(unique=True, max_length=255, nullable=False)
    owner_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", nullable=False)
    
    # Relationships
    owner: "User" = Relationship(back_populates="tables")
    fields: List["Field"] = Relationship(
        back_populates="table", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    shares: List["TableShare"] = Relationship(
        back_populates="table", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    views: List["View"] = Relationship(
        back_populates="table", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )