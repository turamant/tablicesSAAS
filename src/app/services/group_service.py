from decimal import Decimal
from uuid import UUID
from sqlalchemy import text
from src.app.core.database import engine
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.group import GroupRequest, GroupResult, GroupByField, AggregateField
from typing import List, Dict, Any, Optional

class GroupService:
    
    @staticmethod
    def _get_column_name(field_name: str, fields: List[Field]) -> str:
        """Преобразует имя поля в имя колонки в БД"""
        for field in fields:
            if field.name == field_name:
                return f"field_{field.id.hex}"
        return field_name  # если не нашли - возможно id, created_at и т.д.
    
    @staticmethod
    def _get_sql_function(function: str) -> str:
        """Преобразует название функции в SQL"""
        func_map = {
            'sum': 'SUM',
            'avg': 'AVG',
            'count': 'COUNT',
            'min': 'MIN',
            'max': 'MAX'
        }
        return func_map.get(function, 'COUNT')
    
    @classmethod
    async def group_data(
        cls,
        table: Table,
        request: GroupRequest
    ) -> GroupResult:
        """
        Группировка данных с агрегациями
        """
        
        fields = table.fields
        
        # Формируем SELECT часть
        select_parts = []
        group_by_parts = []
        
        # Поля для группировки
        for gb in request.group_by:
            col_name = cls._get_column_name(gb.field, fields)
            select_parts.append(f"{col_name} as {gb.field}")
            group_by_parts.append(col_name)
        
        # Агрегации
        for agg in request.aggregates:
            col_name = cls._get_column_name(agg.field, fields)
            alias = agg.alias or f"{agg.field}_{agg.function}"
            
            if agg.function == 'count' and agg.field == '*':
                select_parts.append(f"COUNT(*) as {alias}")
            elif agg.function in ['sum', 'avg']:
                # Для сумм и средних - округляем сразу в SQL
                if agg.function == 'sum':
                    select_parts.append(f"ROUND(SUM({col_name})::numeric, 0) as {alias}")
                else:  # avg
                    select_parts.append(f"ROUND(AVG({col_name})::numeric, 2) as {alias}")
            elif agg.function == 'min' or agg.function == 'max':
                select_parts.append(f"{agg.function.upper()}({col_name}) as {alias}")
            else:
                sql_func = cls._get_sql_function(agg.function)
                select_parts.append(f"{sql_func}({col_name}) as {alias}")
        
        # Базовый запрос
        query = f"""
            SELECT 
                {', '.join(select_parts)}
            FROM {table.physical_name}
        """
        
        # WHERE (фильтры)
        where_clauses = []
        query_params = {}
        
        if request.filters:
            for i, f in enumerate(request.filters):
                # TODO: добавить обработку фильтров
                pass
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        # GROUP BY
        if group_by_parts:
            query += " GROUP BY " + ", ".join(group_by_parts)
        
        # ORDER BY
        order_parts = []
        for gb in request.group_by:
            col_name = cls._get_column_name(gb.field, fields)
            direction = "DESC" if gb.sort_direction == "desc" else "ASC"
            order_parts.append(f"{col_name} {direction}")
        
        if order_parts:
            query += " ORDER BY " + ", ".join(order_parts)
        
        # Пагинация
        query += f" LIMIT {request.limit} OFFSET {request.offset}"
        
        # Выполняем запрос
        async with engine.connect() as conn:
            result = await conn.execute(text(query), query_params)
            rows = result.mappings().all()
            
            # Получаем общее количество групп
            count_query = f"""
                SELECT COUNT(DISTINCT {', '.join(group_by_parts)}) as total
                FROM {table.physical_name}
            """
            count_result = await conn.execute(text(count_query))
            total = count_result.scalar() or 0
            
            # 🔧 КОНВЕРТАЦИЯ Decimal → float (добавлено)
            groups = []
            for row in rows:
                row_dict = dict(row)
                for key, value in row_dict.items():
                    if isinstance(value, Decimal):
                        row_dict[key] = float(value)
                groups.append(row_dict)
            
            # Общие итоги (опционально)
            grand_totals = {}
            
            return GroupResult(
                groups=groups,
                total_groups=total,
                grand_totals=grand_totals
            )