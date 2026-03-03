from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import text
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.table import TableCreate
from src.app.core.database import engine
import uuid
import re

class TableService:
    @staticmethod
    def generate_physical_name(table_name: str) -> str:
        """Генерирует имя для реальной таблицы в БД"""
        # Очищаем имя от спецсимволов
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '', table_name.lower().replace(' ', '_'))
        return f"data_{uuid.uuid4().hex[:8]}_{clean_name}"

    @staticmethod
    async def create_physical_table(physical_name: str, fields: list) -> None:
        """Создает реальную таблицу в PostgreSQL"""
        # Базовые колонки
        columns = [
            "id UUID PRIMARY KEY DEFAULT gen_random_uuid()",
            "_created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()",
            "_created_by UUID",
            "_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()"
        ]
        
        # Добавляем колонки для каждого поля
        for field in fields:
            col_type = {
                "text": "TEXT",
                "number": "NUMERIC",
                "date": "DATE",
                "boolean": "BOOLEAN",
                "email": "TEXT",
                "select": "TEXT",
                "multiselect": "JSONB"
            }.get(field.field_type.value, "TEXT")
            
            columns.append(f"field_{field.id.hex} {col_type}")
        
        create_sql = f"CREATE TABLE {physical_name} (\n  " + ",\n  ".join(columns) + "\n)"
        
        async with engine.connect() as conn:
            await conn.execute(text(create_sql))
            await conn.commit()

    @classmethod
    async def create_table(cls, session: AsyncSession, user_id: str, table_data: TableCreate) -> Table:
        """Создает новую таблицу"""
        # Создаем запись в мета-таблице
        physical_name = cls.generate_physical_name(table_data.name)
        
        db_table = Table(
            name=table_data.name,
            description=table_data.description,
            physical_name=physical_name,
            owner_id=user_id
        )
        session.add(db_table)
        await session.flush()  # чтобы получить id
        
        # Создаем поля
        fields = []
        for field_data in table_data.fields:
            db_field = Field(
                table_id=db_table.id,
                name=field_data.name,
                display_name=field_data.display_name,
                field_type=field_data.field_type,
                is_required=field_data.is_required,
                is_unique=field_data.is_unique,
                options=field_data.options,
                sort_order=field_data.sort_order
            )
            session.add(db_field)
            fields.append(db_field)
        
        await session.flush()
        
        # Создаем реальную таблицу в БД
        await cls.create_physical_table(physical_name, fields)
        
        await session.commit()
        await session.refresh(db_table)
        
        return db_table