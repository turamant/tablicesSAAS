"""add formula field type

Revision ID: 41be8bec823c
Revises: b22325a3420d
Create Date: 2026-03-07 16:28:37.568479

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision: str = '41be8bec823c'
down_revision: Union[str, Sequence[str], None] = 'b22325a3420d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Имя enum типа в PostgreSQL
ENUM_NAME = 'fieldtype'

def upgrade() -> None:
    """Upgrade schema."""
    # Создаем новый enum тип с добавленным 'formula'
    new_enum = ENUM(
        'text', 'number', 'date', 'boolean', 
        'select', 'multiselect', 'email', 'formula',
        name=ENUM_NAME,
        create_type=False
    )
    
    # Изменяем тип колонки
    op.execute(f"ALTER TABLE fields ALTER COLUMN field_type TYPE {ENUM_NAME} USING field_type::text::{ENUM_NAME}")


def downgrade() -> None:
    """Downgrade schema."""
    # Возвращаем старый enum без 'formula'
    old_enum = ENUM(
        'text', 'number', 'date', 'boolean', 
        'select', 'multiselect', 'email',
        name=ENUM_NAME,
        create_type=False
    )
    
    # Сначала нужно обновить данные, убрать formula значения
    op.execute("UPDATE fields SET field_type = 'text' WHERE field_type = 'formula'")
    
    # Изменяем тип обратно
    op.execute(f"ALTER TABLE fields ALTER COLUMN field_type TYPE {ENUM_NAME} USING field_type::text::{ENUM_NAME}")