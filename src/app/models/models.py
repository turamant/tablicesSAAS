from sqlmodel import SQLModel, Field, Relationship, Column, DateTime, String, Boolean, JSON
from sqlalchemy import func, Enum as SQLEnum
from datetime import datetime
import uuid
from typing import Optional, List, TYPE_CHECKING
import enum

# === Перечисления ===

class SharePermission(str, enum.Enum):
    READ = "read"
    EDIT = "edit"
    ADMIN = "admin"

class FieldType(str, enum.Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    SELECT = "select"
    MULTISELECT = "multiselect"
    EMAIL = "email"

# === Модели ===

class User(SQLModel, table=True):
    __tablename__ = "users"
    __allow_unmapped__ = True  # ВАЖНО!
    
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
    
    email: str = Field(unique=True, index=True, max_length=255, nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    full_name: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    
    # Relationships
    tables: List["Table"] = Relationship(back_populates="owner", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    refresh_tokens: List["RefreshToken"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Table(SQLModel, table=True):
    __tablename__ = "tables"
    __allow_unmapped__ = True  # ВАЖНО!
    
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
    fields: List["Field"] = Relationship(back_populates="table", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    shares: List["TableShare"] = Relationship(back_populates="table", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Field(SQLModel, table=True):
    __tablename__ = "fields"
    __allow_unmapped__ = True  # ВАЖНО!
    
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


class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    __allow_unmapped__ = True  # ВАЖНО!
    
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
    
    token: str = Field(unique=True, index=True, max_length=512, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="users.id", ondelete="CASCADE", nullable=False)
    expires_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )
    is_revoked: bool = Field(default=False)
    user_agent: Optional[str] = Field(default=None, max_length=255)
    ip_address: Optional[str] = Field(default=None, max_length=50)
    
    # Relationships
    user: "User" = Relationship(back_populates="refresh_tokens")


class TableShare(SQLModel, table=True):
    __tablename__ = "table_shares"
    __allow_unmapped__ = True  # ВАЖНО!
    
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