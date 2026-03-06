from typing import List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, update
from sqlalchemy.orm import selectinload
from src.app.models.table import Table
from src.app.models.view import View
from src.app.schemas.view import ViewCreate, ViewResponse
from fastapi import HTTPException

class ViewService:
    
    @staticmethod
    async def check_table_access(
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
    
    @classmethod
    async def create_view(
        cls,
        table_id: UUID,
        view_data: ViewCreate,
        session: AsyncSession,
        user_id: str
    ) -> View:
        """Создание нового представления"""
        # Проверяем доступ
        await cls.check_table_access(table_id, session, user_id)
        
        # Если это представление по умолчанию, сбрасываем у других
        if view_data.is_default:
            await session.execute(
                update(View)
                .where(View.table_id == table_id)
                .values(is_default=False)
            )
        
        # Создаем представление
        view = View(
            **view_data.dict(),
            created_by=user_id
        )
        session.add(view)
        await session.commit()
        await session.refresh(view)
        
        return view
    
    @classmethod
    async def get_views(
        cls,
        table_id: UUID,
        session: AsyncSession,
        user_id: str
    ) -> List[View]:
        """Получение всех представлений таблицы"""
        await cls.check_table_access(table_id, session, user_id)
        
        result = await session.execute(
            select(View).where(View.table_id == table_id)
        )
        return result.scalars().all()
    
    @classmethod
    async def get_view(
        cls,
        table_id: UUID,
        view_id: UUID,
        session: AsyncSession,
        user_id: str
    ) -> View:
        """Получение конкретного представления"""
        await cls.check_table_access(table_id, session, user_id)
        
        view = await session.get(View, view_id)
        if not view or view.table_id != table_id:
            raise HTTPException(status_code=404, detail="View not found")
        
        return view
    
    @classmethod
    async def update_view(
        cls,
        table_id: UUID,
        view_id: UUID,
        view_data: ViewCreate,
        session: AsyncSession,
        user_id: str
    ) -> View:
        """Обновление представления"""
        await cls.check_table_access(table_id, session, user_id)
        
        view = await session.get(View, view_id)
        if not view or view.table_id != table_id:
            raise HTTPException(status_code=404, detail="View not found")
        
        # Если это представление по умолчанию, сбрасываем у других
        if view_data.is_default and not view.is_default:
            await session.execute(
                update(View)
                .where(View.table_id == table_id)
                .values(is_default=False)
            )
        
        # Обновляем
        for key, value in view_data.dict().items():
            setattr(view, key, value)
        
        await session.commit()
        await session.refresh(view)
        
        return view
    
    @classmethod
    async def delete_view(
        cls,
        table_id: UUID,
        view_id: UUID,
        session: AsyncSession,
        user_id: str
    ) -> None:
        """Удаление представления"""
        await cls.check_table_access(table_id, session, user_id)
        
        view = await session.get(View, view_id)
        if not view or view.table_id != table_id:
            raise HTTPException(status_code=404, detail="View not found")
        
        await session.delete(view)
        await session.commit()