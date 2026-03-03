from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, DateTime, func
from datetime import datetime
import uuid
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class RefreshToken(SQLModel, table=True):
    __tablename__ = "refresh_tokens"
    
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