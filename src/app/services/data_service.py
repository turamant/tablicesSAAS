from sqlalchemy import text
from src.app.core.database import engine
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.data import DataQueryParams, DataFilter
from uuid import UUID
from typing import Dict, Any, List, Optional
import json
import uuid

class DataService:
    @staticmethod
    def _get_column_name(field_name: str, fields: List[Field]) -> str:
        """Преобразует имя поля в имя колонки в БД"""
        # Если это уже field_xxx, возвращаем как есть
        if field_name.startswith("field_") and len(field_name) == 41:  # field_ + 32 hex = 41
            return field_name
        
        # Если это стандартное поле
        if field_name in ["id", "_created_at", "_created_by", "_updated_at"]:
            return field_name
        
        # Ищем поле по имени
        for field in fields:
            if field.name == field_name:
                return f"field_{field.id.hex}"
        
        # Если не нашли, возвращаем как есть (будет ошибка)
        return field_name

    @staticmethod
    async def validate_data(table: Table, fields: List[Field], data: Dict[str, Any]) -> Dict[str, Any]:
        """Валидирует и преобразует данные под типы полей"""
        # Создаем маппинг имени поля на объект Field
        field_by_name = {f.name: f for f in fields}
        field_by_id = {str(f.id): f for f in fields}
        
        validated = {}
        
        for key, value in data.items():
            # Пробуем найти поле по имени
            field = field_by_name.get(key)
            
            # Если не нашли по имени, пробуем по ID
            if not field:
                field = field_by_id.get(key)
            
            if not field:
                raise ValueError(f"Field '{key}' not found in table")
            
            col_name = f"field_{field.id.hex}"
            
            # Валидация по типу
            if value is None:
                if field.is_required:
                    raise ValueError(f"Field {field.name} is required")
                validated[col_name] = None
                continue
            
            if field.field_type in ["text", "email", "select"]:
                validated[col_name] = str(value)
            elif field.field_type == "number":
                try:
                    validated[col_name] = float(value)
                except ValueError:
                    raise ValueError(f"Field {field.name} must be a number")
            elif field.field_type == "boolean":
                validated[col_name] = bool(value)
            elif field.field_type == "date":
                validated[col_name] = str(value)
            elif field.field_type == "multiselect":
                validated[col_name] = json.dumps(value) if isinstance(value, list) else str(value)
        
        return validated

    @classmethod
    async def create_record(cls, table: Table, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает запись в динамической таблице"""
        fields = table.fields
        validated_data = await cls.validate_data(table, fields, data)
        
        columns = ["id", "_created_by"] + list(validated_data.keys())
        placeholders = [":id", ":user_id"] + [f":{k}" for k in validated_data.keys()]
        
        query = f"""
            INSERT INTO {table.physical_name} 
            ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """
        
        params = {
            "id": uuid.uuid4(),
            "user_id": UUID(user_id) if isinstance(user_id, str) else user_id,
            **validated_data
        }
        
        async with engine.connect() as conn:
            result = await conn.execute(text(query), params)
            await conn.commit()
            row = result.mappings().first()
            
            # Преобразуем ответ в человеческий вид
            return cls._format_record(dict(row), fields)

    @classmethod
    async def get_records(
        cls, 
        table: Table, 
        user_id: str, 
        params: DataQueryParams
    ) -> List[Dict[str, Any]]:
        """Получает записи с фильтрацией"""
        fields = table.fields
        field_map = {f"field_{f.id.hex}": f for f in fields}
        
        # Базовый запрос
        query = f"SELECT * FROM {table.physical_name}"
        where_clauses = []
        query_params = {}
        
        # Добавляем фильтры
        if params.filters:
            for i, f in enumerate(params.filters):
                # Преобразуем имя поля в имя колонки
                column_name = cls._get_column_name(f.field, fields)
                
                operator_map = {
                    "eq": "=",
                    "ne": "!=",
                    "gt": ">",
                    "lt": "<",
                    "gte": ">=",
                    "lte": "<=",
                    "like": "LIKE",
                    "in": "IN"
                }
                
                op = operator_map.get(f.operator)
                if op:
                    param_name = f"p_{i}"
                    if f.operator == "in":
                        placeholders = ', '.join([f":{param_name}_{j}" for j in range(len(f.value))])
                        where_clauses.append(f"{column_name} IN ({placeholders})")
                        for j, val in enumerate(f.value):
                            query_params[f"{param_name}_{j}"] = val
                    else:
                        where_clauses.append(f"{column_name} {op} :{param_name}")
                        query_params[param_name] = f.value
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # Сортировка
        if params.order_by:
            # Преобразуем имя поля в имя колонки
            order_column = cls._get_column_name(params.order_by, fields)
            direction = "DESC" if params.order_direction.lower() == "desc" else "ASC"
            query += f" ORDER BY {order_column} {direction}"
        
        # Пагинация
        query += f" LIMIT {params.limit} OFFSET {params.offset}"
        
        async with engine.connect() as conn:
            result = await conn.execute(text(query), query_params)
            rows = result.mappings().all()
            
            # Преобразуем каждую запись в человеческий вид
            records = []
            for row in rows:
                records.append(cls._format_record(dict(row), fields))
            
            return records

    @classmethod
    async def get_record(
        cls,
        table: Table,
        record_id: UUID,
        user_id: str
    ) -> Optional[Dict[str, Any]]:
        """Получает одну запись по ID"""
        fields = table.fields
        
        query = f"SELECT * FROM {table.physical_name} WHERE id = :id"
        
        async with engine.connect() as conn:
            result = await conn.execute(text(query), {"id": record_id})
            row = result.mappings().first()
            
            if not row:
                return None
            
            return cls._format_record(dict(row), fields)

    @classmethod
    async def update_record(
        cls, 
        table: Table, 
        record_id: UUID, 
        user_id: str, 
        data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Обновляет запись"""
        fields = table.fields
        validated_data = await cls.validate_data(table, fields, data)
        
        if not validated_data:
            return None
        
        set_clause = ", ".join([f"{k} = :{k}" for k in validated_data.keys()])
        set_clause += ", _updated_at = NOW()"
        
        query = f"""
            UPDATE {table.physical_name}
            SET {set_clause}
            WHERE id = :id
            RETURNING *
        """
        
        params = {
            "id": record_id,
            **validated_data
        }
        
        async with engine.connect() as conn:
            result = await conn.execute(text(query), params)
            await conn.commit()
            row = result.mappings().first()
            
            if not row:
                return None
            
            return cls._format_record(dict(row), fields)

    @classmethod
    async def delete_record(cls, table: Table, record_id: UUID) -> bool:
        """Удаляет запись"""
        query = f"DELETE FROM {table.physical_name} WHERE id = :id RETURNING id"
        
        async with engine.connect() as conn:
            result = await conn.execute(text(query), {"id": record_id})
            await conn.commit()
            return result.rowcount > 0

    @staticmethod
    def _format_record(record: Dict[str, Any], fields: List[Field]) -> Dict[str, Any]:
        """Преобразует запись из БД в человеческий вид"""
        field_by_column = {f"field_{f.id.hex}": f for f in fields}
        
        formatted = {
            "id": record["id"],
            "_created_at": record["_created_at"],
            "_created_by": record["_created_by"],
            "_updated_at": record["_updated_at"]
        }
        
        # Добавляем все поля с человеческими именами
        for key, value in record.items():
            if key.startswith("field_"):
                field = field_by_column.get(key)
                if field:
                    formatted[field.name] = value
                else:
                    formatted[key] = value
        
        return formatted