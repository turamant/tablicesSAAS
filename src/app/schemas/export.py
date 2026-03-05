from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

class ExportOptions(BaseModel):
    """Опции экспорта"""
    format: str = "excel"  # excel, csv
    include_aggregations: bool = False
    include_metadata: bool = True
    fields: Optional[List[str]] = None  # список полей для экспорта