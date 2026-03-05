from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, File
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.database import get_session
from src.app.models.table import Table
from src.app.services.import_service import ImportService
from src.app.schemas.import_data import ImportPreview, ImportRequest
from src.app.api.dependencies import get_current_user_id
from uuid import UUID

router = APIRouter(prefix="/tables/{table_id}/import", tags=["import"])

@router.post("/preview")
async def preview_import(
    table_id: UUID,
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Предпросмотр Excel файла перед импортом"""
    # Проверяем доступ
    result = await session.execute(
        select(Table)
        .where(Table.id == table_id)
        .options(selectinload(Table.fields))
    )
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if str(table.owner_id) != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    # Проверяем тип файла
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    
    # Читаем файл
    content = await file.read()
    
    # Предпросмотр
    preview = await ImportService.preview_excel(content, table)
    
    return preview

@router.post("/")
async def import_data(
    table_id: UUID,
    file: UploadFile = File(...),
    mappings: str = Form(...),  # JSON строка
    skip_first_row: bool = Form(True),
    create_missing_fields: bool = Form(False),
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Импорт данных из Excel"""
    # Проверяем доступ
    result = await session.execute(
        select(Table)
        .where(Table.id == table_id)
        .options(selectinload(Table.fields))
    )
    table = result.scalar_one_or_none()
    
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    
    if str(table.owner_id) != user_id:
        raise HTTPException(status_code=403, detail="Not owner")
    
    # Парсим mappings из JSON
    import json
    mappings_data = json.loads(mappings)
    
    # Читаем файл
    content = await file.read()
    
    # Импортируем
    result = await ImportService.import_excel(
        file_content=content,
        table=table,
        mappings=mappings_data,
        user_id=user_id,
        session=session,  # ← Передаем сессию!
        skip_first_row=skip_first_row,
        create_missing_fields=create_missing_fields
    )
    
    return result