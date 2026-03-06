# src/app/services/import_service.py

import io
import re
import logging
import pandas as pd
from typing import List, Dict, Any, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.app.schemas.field import FieldCreate
from src.app.models.table import Table
from src.app.models.field import Field
from src.app.schemas.import_data import FieldMapping, ImportPreview
from src.app.services.data_service import DataService
from src.app.services.field_service import FieldService

logger = logging.getLogger(__name__)


class ImportService:
    
    @staticmethod
    async def preview_excel(
        file_content: bytes,
        table: Table
    ) -> ImportPreview:
        """
        Предпросмотр Excel файла перед импортом.
        Возвращает заголовки, первые 5 строк данных и предполагаемый маппинг полей.
        """
        try:
            df = pd.read_excel(io.BytesIO(file_content), header=None)
            
            if df.empty:
                return ImportPreview(
                    columns=[],
                    rows=[],
                    total_rows=0,
                    suggested_mappings=[]
                )
            
            # Первая строка — заголовки
            columns = [str(col).strip() for col in df.iloc[0].fillna('')]
            
            # Данные: первые 5 строк (после заголовков)
            rows = []
            for idx in range(1, min(6, len(df))):
                row_values = df.iloc[idx].fillna('')
                row_dict = {
                    columns[col_idx]: str(val) if pd.notna(val) else ''
                    for col_idx, val in enumerate(row_values)
                    if col_idx < len(columns)
                }
                rows.append(row_dict)
            
            # Авто-маппинг: ищем совпадения по display_name (регистронезависимо)
            table_fields = {
                f.display_name.lower().strip(): f.name
                for f in table.fields
            }
            
            suggested_mappings = []
            for col in columns:
                col_normalized = col.lower().strip()
                matched_field = table_fields.get(col_normalized)
                
                suggested_mappings.append(FieldMapping(
                    excel_column=col,
                    table_field=matched_field or "",
                    skip=matched_field is None
                ))
            
            return ImportPreview(
                columns=columns,
                rows=rows,
                total_rows=max(0, len(df) - 1),
                suggested_mappings=suggested_mappings
            )
            
        except Exception as e:
            logger.error(f"Preview error: {e}", exc_info=True)
            raise

    @classmethod
    async def import_excel(
        cls,
        file_content: bytes,
        table: Table,
        mappings: List[Dict[str, Any]],
        user_id: str,
        session: AsyncSession,
        skip_first_row: bool = True,
        create_missing_fields: bool = False
    ) -> Dict[str, Any]:
        """
        Импорт данных из Excel-файла в таблицу.
        
        :param file_content: байты Excel-файла
        :param table: целевая таблица
        :param mappings: список маппингов колонок
        :param user_id: ID пользователя, выполняющего импорт
        :param session: асинхронная сессия БД
        :param skip_first_row: пропускать ли первую строку как заголовки
        :param create_missing_fields: создавать ли новые поля при отсутствии
        :return: статистика импорта
        """
        logger.info(
            f"Starting import for table={table.id}, user={user_id}, "
            f"create_missing_fields={create_missing_fields}"
        )
        
        try:
            # === 1. Чтение и предобработка данных ===
            df = pd.read_excel(
                io.BytesIO(file_content),
                header=0 if skip_first_row else None
            )
            df = df.dropna(how='all')  # убираем полностью пустые строки
            
            # Фильтруем строки с итоговыми значениями
            if not df.empty and df.shape[1] > 0:
                first_col = df.iloc[:, 0].astype(str).str.lower()
                df = df[~first_col.str.contains(r'итого|всего|total|сумма', na=False, regex=True)]
            
            if df.empty:
                logger.warning("No data rows found after preprocessing")
                return {"imported": 0, "total": 0, "errors": ["No valid data rows found"]}
            
            # === 2. Парсинг маппингов ===
            mapping_objects = [FieldMapping(**m) for m in mappings]
            active_mappings = [m for m in mapping_objects if not m.skip]
            
            if not active_mappings:
                return {
                    "imported": 0,
                    "total": len(df),
                    "errors": ["No columns selected for import"]
                }
            
            # === 3. Построение маппинга: Excel-колонка → техническое имя поля ===
            column_mapping: Dict[str, str] = {}
            
            # 3.1. Сначала ищем существующие поля
            for m in active_mappings:
                matched_field = None
                
                # Поиск по display_name (регистронезависимый)
                if m.excel_column:
                    matched_field = next(
                        (
                            f for f in table.fields
                            if f.display_name.lower().strip() == m.excel_column.lower().strip()
                        ),
                        None
                    )
                
                # Если не нашли, но фронт явно указал table_field — проверяем по name
                if not matched_field and m.table_field:
                    matched_field = next(
                        (f for f in table.fields if f.name == m.table_field),
                        None
                    )
                
                if matched_field:
                    column_mapping[m.excel_column] = matched_field.name
                    logger.debug(f"Mapped '{m.excel_column}' → existing field '{matched_field.name}'")
            
            # 3.2. Создаём недостающие поля (если разрешено)
            if create_missing_fields:
                existing_names = {f.name for f in table.fields}
                
                for m in active_mappings:
                    if m.excel_column in column_mapping:
                        continue  # уже замаплено на существующее поле
                    
                    # Генерация технического имени
                    tech_name = (m.table_field or m.excel_column or "").strip()
                    if not tech_name:
                        logger.warning(f"Skipping column '{m.excel_column}': empty field name")
                        continue
                    
                    tech_name = cls._normalize_field_name(tech_name)
                    
                    if not tech_name or tech_name in existing_names:
                        continue
                    
                    try:
                        field_create = FieldCreate(
                            name=tech_name,
                            display_name=m.excel_column,
                            field_type="text",
                            is_required=False,
                            options=None
                        )
                        
                        new_field = await FieldService.create_field(
                            session=session,
                            table=table,
                            field_data=field_create
                        )
                        
                        column_mapping[m.excel_column] = tech_name
                        existing_names.add(tech_name)
                        table.fields.append(new_field)  # обновляем кэш в памяти
                        
                        logger.info(f"Created new field: '{tech_name}' for column '{m.excel_column}'")
                        
                    except IntegrityError as e:
                        logger.warning(f"Could not create field '{tech_name}': {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Unexpected error creating field '{tech_name}': {e}", exc_info=True)
                        continue
            
            # === 4. Импорт записей ===
            imported = 0
            errors: List[str] = []
            
            for idx, row in df.iterrows():
                try:
                    record_data = {}
                    
                    for col_name, value in row.items():
                        if col_name not in column_mapping:
                            continue
                        
                        field_name = column_mapping[col_name]
                        record_data[field_name] = None if pd.isna(value) else value
                    
                    if not record_data:
                        continue
                    
                    await DataService.create_record(
                        table=table,
                        user_id=user_id,
                        data=record_data
                    )
                    imported += 1
                    
                except Exception as e:
                    error_msg = f"Row {idx + (2 if skip_first_row else 1)}: {cls._safe_str(e)}"
                    errors.append(error_msg)
                    logger.warning(f"Import error: {error_msg}")
            
            logger.info(
                f"Import completed: {imported}/{len(df)} rows succeeded, "
                f"{len(errors)} errors"
            )
            
            return {
                "imported": imported,
                "total": len(df),
                "errors": errors[:50]  # ограничиваем вывод ошибок для безопасности
            }
            
        except pd.errors.EmptyDataError:
            logger.error("Empty Excel file provided")
            return {"imported": 0, "total": 0, "errors": ["File is empty or invalid"]}
        except Exception as e:
            logger.error(f"Critical import error: {e}", exc_info=True)
            raise

    @staticmethod
    def _normalize_field_name(name: str) -> str:
        """
        Нормализует имя поля: приводит к lowercase, заменяет спецсимволы на _, 
        убирает дубликаты подчёркиваний и обрезает крайние _.
        """
        name = name.lower().strip()
        name = re.sub(r'[^a-z0-9а-яё_]', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        return name

    @staticmethod
    def _safe_str(obj: Any, max_len: int = 200) -> str:
        """Безопасное преобразование объекта в строку для логирования."""
        try:
            s = str(obj)
            return s[:max_len] + ("..." if len(s) > max_len else "")
        except Exception:
            return f"<unprintable {type(obj).__name__}>"