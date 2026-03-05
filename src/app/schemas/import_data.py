from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID

class FieldMapping(BaseModel):
    """Маппинг полей из Excel в поля таблицы"""
    excel_column: str  # название колонки в Excel
    table_field: str   # имя поля в таблице
    skip: bool = False # пропустить эту колонку

class ImportPreview(BaseModel):
    """Предпросмотр импорта"""
    columns: List[str]  # колонки в Excel
    rows: List[Dict[str, Any]]  # первые 5 строк для предпросмотра
    total_rows: int
    suggested_mappings: List[FieldMapping]  # предполагаемый маппинг

class ImportRequest(BaseModel):
    """Запрос на импорт"""
    mappings: List[FieldMapping]  # как маппить колонки
    skip_first_row: bool = True  # пропустить заголовок
    create_missing_fields: bool = False  # создавать недостающие поля