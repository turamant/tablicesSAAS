import io
import pandas as pd
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.import_data import FieldMapping, ImportPreview
from src.app.services.data_service import DataService
from src.app.services.field_service import FieldService

class ImportService:
    
    @staticmethod
    async def preview_excel(
        file_content: bytes,
        table: Table
    ) -> ImportPreview:
        """
        Предпросмотр Excel файла перед импортом
        """
        # Читаем Excel
        df = pd.read_excel(io.BytesIO(file_content), header=None)
        
        # Получаем колонки (первая строка как заголовки)
        columns = df.iloc[0].astype(str).tolist() if len(df) > 0 else []
        
        # Получаем первые 5 строк данных
        rows = []
        for idx in range(1, min(6, len(df))):
            row = df.iloc[idx].tolist()
            row_dict = {}
            for col_idx, col_name in enumerate(columns):
                if col_idx < len(row):
                    row_dict[col_name] = str(row[col_idx]) if pd.notna(row[col_idx]) else ''
            rows.append(row_dict)
        
        # Предполагаемый маппинг (ищем похожие имена)
        suggested_mappings = []
        table_fields = {f.display_name.lower(): f.name for f in table.fields}
        
        for col in columns:
            col_lower = col.lower().strip()
            matched = False
            
            for field_display, field_name in table_fields.items():
                if col_lower in field_display or field_display in col_lower:
                    suggested_mappings.append(FieldMapping(
                        excel_column=col,
                        table_field=field_name,
                        skip=False
                    ))
                    matched = True
                    break
            
            if not matched:
                suggested_mappings.append(FieldMapping(
                    excel_column=col,
                    table_field="",
                    skip=True
                ))
        
        return ImportPreview(
            columns=columns,
            rows=rows,
            total_rows=len(df) - 1,
            suggested_mappings=suggested_mappings
        )
    
    @classmethod
    async def import_excel(
        cls,
        file_content: bytes,
        table: Table,
        mappings: List[dict],  # ← Важно: List[dict], а не List[FieldMapping]
        user_id: str,
        session: AsyncSession,  # ← Добавляем сессию
        skip_first_row: bool = True,
        create_missing_fields: bool = False
    ) -> Dict[str, any]:
        """
        Импорт данных из Excel в таблицу
        """
        # Читаем Excel
        df = pd.read_excel(io.BytesIO(file_content), header=0 if skip_first_row else None)
        # Удаляем пустые строки внизу (где все значения NaN)
        df = df.dropna(how='all')

        # Удаляем строки где первая колонка содержит "ИТОГО" или "Всего"
        df = df[~df.iloc[:, 0].astype(str).str.contains('ИТОГО|Всего|Total', na=False)]
        
        # Преобразуем словари в объекты FieldMapping
        mapping_objects = [FieldMapping(**m) for m in mappings]
        
        # Создаем маппинг колонок
        column_mapping = {}
        for m in mapping_objects:
            if not m.skip and m.table_field:
                column_mapping[m.excel_column] = m.table_field
        
        # Создаем недостающие поля если нужно
        if create_missing_fields:
            existing_fields = {f.name for f in table.fields}
            for col, field_name in column_mapping.items():
                if field_name not in existing_fields:
                    # Создаем новое поле
                    new_field_data = {
                        "name": field_name,
                        "display_name": col,
                        "field_type": "text",  # по умолчанию текст
                        "is_required": False
                    }
                    
                    # Используем FieldService для создания поля
                    # Примечание: FieldService.create_field должен принимать session
                    from src.app.schemas.field import FieldCreate
                    field_create = FieldCreate(**new_field_data)
                    
                    # TODO: добавить создание поля через FieldService
                    # await FieldService.create_field(session, table.id, field_create, user_id)
        
        # Импортируем данные
        imported = 0
        errors = []
        
        for idx, row in df.iterrows():
            try:
                record_data = {}
                for col, value in row.items():
                    if col in column_mapping:
                        field_name = column_mapping[col]
                        # Преобразуем NaN в None
                        if pd.isna(value):
                            record_data[field_name] = None
                        else:
                            # Конвертируем в нужный тип в зависимости от поля
                            record_data[field_name] = value
                
                if record_data:
                    # Создаем запись через DataService
                    await DataService.create_record(table, user_id, record_data)
                    imported += 1
                    
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        return {
            "imported": imported,
            "total": len(df),
            "errors": errors
        }