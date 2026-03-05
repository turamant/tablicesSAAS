from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.orm import selectinload
from src.app.core.database import get_session
from src.app.models.table import Table
from src.app.schemas.group import GroupRequest, GroupResult
from src.app.services.group_service import GroupService
from src.app.api.dependencies import get_current_user_id
from uuid import UUID

router = APIRouter(prefix="/tables/{table_id}/group", tags=["group"])

@router.post("/", response_model=GroupResult)
async def group_data(
    table_id: UUID,
    request: GroupRequest,
    session: AsyncSession = Depends(get_session),
    user_id: str = Depends(get_current_user_id)
):
    """Сгруппировать данные с агрегациями"""
    # Проверяем доступ к таблице
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
    
    # Выполняем группировку
    grouped = await GroupService.group_data(table, request)
    
    return grouped