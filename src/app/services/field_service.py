from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy import text
from src.app.core.database import engine
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.field import FieldCreate, FieldUpdate
from fastapi import HTTPException
from typing import List, Optional

class FieldService:
    
    @staticmethod
    async def get_table_and_check_access(
        table_id: UUID,
        session: AsyncSession,
        user_id: str
    ) -> Table:
        """Проверка доступа к таблице"""
        result = await session.execute(
            select(Table).where(Table.id == table_id)
        )
        table = result.scalar_one_or_none()
        
        if not table:
            raise HTTPException(status_code=404, detail="Table not found")
        
        if str(table.owner_id) != user_id:
            raise HTTPException(status_code=403, detail="Not owner")
        
        return table

    @staticmethod
    def _get_sql_type(field_type: str) -> str:
        """Маппинг типов полей в типы PostgreSQL"""
        type_map = {
            "text": "TEXT",
            "number": "NUMERIC",
            "date": "DATE",
            "boolean": "BOOLEAN",
            "email": "TEXT",
            "select": "TEXT",
            "multiselect": "JSONB"
        }
        return type_map.get(field_type, "TEXT")

    @classmethod
    async def create_field(
        cls,
        table: Table,
        field_data: FieldCreate,
        session: AsyncSession
    ) -> Field:
        """Создание нового поля"""
        # Создаем поле в мета-таблице
        new_field = Field(
            table_id=table.id,
            name=field_data.name,
            display_name=field_data.display_name,
            field_type=field_data.field_type,
            is_required=field_data.is_required,
            is_unique=field_data.is_unique,
            options=field_data.options,
            sort_order=field_data.sort_order
        )
        session.add(new_field)
        await session.flush()
        
        # Добавляем колонку в физическую таблицу
        col_name = f"field_{new_field.id.hex}"
        col_type = cls._get_sql_type(field_data.field_type)
        
        async with engine.connect() as conn:
            await conn.execute(text(
                f"ALTER TABLE {table.physical_name} ADD COLUMN {col_name} {col_type}"
            ))
            await conn.commit()
        
        await session.commit()
        await session.refresh(new_field)
        
        return new_field

    @classmethod
    async def delete_field(
        cls,
        table: Table,
        field_id: UUID,
        session: AsyncSession
    ) -> None:
        """Удаление поля"""
        # Проверяем что поле существует
        result = await session.execute(
            select(Field).where(
                Field.id == field_id,
                Field.table_id == table.id
            )
        )
        field = result.scalar_one_or_none()
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Удаляем колонку из физической таблицы
        col_name = f"field_{field.id.hex}"
        async with engine.connect() as conn:
            await conn.execute(text(
                f"ALTER TABLE {table.physical_name} DROP COLUMN {col_name}"
            ))
            await conn.commit()
        
        # Удаляем мета-запись
        await session.delete(field)
        await session.commit()

    @classmethod
    async def update_field(
        cls,
        table: Table,
        field_id: UUID,
        field_data: FieldUpdate,
        session: AsyncSession
    ) -> Field:
        """Обновление поля (без изменения типа)"""
        result = await session.execute(
            select(Field).where(
                Field.id == field_id,
                Field.table_id == table.id
            )
        )
        field = result.scalar_one_or_none()
        
        if not field:
            raise HTTPException(status_code=404, detail="Field not found")
        
        # Обновляем только разрешенные поля
        if field_data.name is not None:
            field.name = field_data.name
        if field_data.display_name is not None:
            field.display_name = field_data.display_name
        if field_data.is_required is not None:
            field.is_required = field_data.is_required
        
        await session.commit()
        await session.refresh(field)
        
        return field

    @classmethod
    async def get_fields(
        cls,
        table: Table,
        session: AsyncSession
    ) -> List[Field]:
        """Получение всех полей таблицы"""
        result = await session.execute(
            select(Field)
            .where(Field.table_id == table.id)
            .order_by(Field.sort_order)
        )
        return result.scalars().all()