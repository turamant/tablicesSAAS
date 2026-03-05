from uuid import UUID
from sqlalchemy import text
from src.app.core.database import engine
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.aggregate import AggregateResponse
from typing import List, Optional

class AggregateService:
    
    @staticmethod
    async def get_aggregations(
        table: Table,
        fields: Optional[List[str]] = None
    ) -> AggregateResponse:
        """
        Получить агрегации для таблицы
        - COUNT(*) всегда
        - Для числовых полей: SUM, AVG, MIN, MAX
        """
        # Получаем все числовые поля таблицы
        numeric_fields = [
            f for f in table.fields 
            if f.field_type == 'number'
        ]
        
        # Фильтруем по запрошенным полям (если указаны)
        target_fields = numeric_fields
        if fields:
            target_fields = [
                f for f in numeric_fields 
                if f.name in fields
            ]
        
        # Если нет числовых полей - только COUNT
        if not target_fields:
            query = f"SELECT COUNT(*) as total FROM {table.physical_name}"
            
            async with engine.connect() as conn:
                result = await conn.execute(text(query))
                row = result.mappings().first()
                
                return AggregateResponse(
                    total_records=row['total']
                )
        
        # Строим SQL с агрегациями
        select_parts = ["COUNT(*) as total_records"]
        
        for field in target_fields:
            col_name = f"field_{field.id.hex}"
            select_parts.extend([
                f"SUM({col_name}) as sum_{field.name}",
                f"AVG({col_name}) as avg_{field.name}",
                f"MIN({col_name}) as min_{field.name}",
                f"MAX({col_name}) as max_{field.name}"
            ])
        
        query = f"""
            SELECT {', '.join(select_parts)}
            FROM {table.physical_name}
        """
        
        async with engine.connect() as conn:
            result = await conn.execute(text(query))
            row = result.mappings().first()
            
            if not row:
                return AggregateResponse(total_records=0)
            
            # Формируем ответ
            response = AggregateResponse(
                total_records=row['total_records']
            )
            
            for field in target_fields:
                if f"sum_{field.name}" in row and row[f"sum_{field.name}"] is not None:
                    response.sums[field.name] = float(row[f"sum_{field.name}"])
                
                if f"avg_{field.name}" in row and row[f"avg_{field.name}"] is not None:
                    response.averages[field.name] = float(row[f"avg_{field.name}"])
                
                if f"min_{field.name}" in row and row[f"min_{field.name}"] is not None:
                    response.mins[field.name] = float(row[f"min_{field.name}"])
                
                if f"max_{field.name}" in row and row[f"max_{field.name}"] is not None:
                    response.maxs[field.name] = float(row[f"max_{field.name}"])
            
            return response