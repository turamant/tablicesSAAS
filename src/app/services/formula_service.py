import re
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from typing import Any, Dict, Optional, Union
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

class FormulaService:
    
    # Константы
    DATE_FORMATS = ["%Y-%m-%d", "%d.%m.%Y", "%Y/%m/%d"]
    
    @classmethod
    async def evaluate(cls, formula: str, data: Dict[str, Any]) -> Any:
        """
        Универсальное вычисление формул
        """
        if not formula:
            return None
        
        logger.debug(f"Evaluating formula: {formula}")
        
        # Определяем тип формулы по префиксу
        if formula.startswith('DATEDIFF'):
            return await cls._handle_datediff(formula, data)
        
        if formula.startswith('CONCAT'):
            return await cls._handle_concat(formula, data)
        
        # Арифметические выражения
        return await cls._handle_arithmetic(formula, data)
    
    @classmethod
    async def _parse_date(cls, value: Any) -> Optional[date]:
        """Универсальный парсер дат"""
        if value is None:
            return None
            
        if isinstance(value, (date, datetime)):
            return value if isinstance(value, date) else value.date()
        
        if isinstance(value, str):
            for fmt in cls.DATE_FORMATS:
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
        
        logger.warning(f"Could not parse date: {value}")
        return None
    
    @classmethod
    async def _handle_datediff(cls, expr: str, data: Dict[str, Any]) -> Optional[str]:
        """Оптимизированная обработка DATEDIFF"""
        # Парсим одним регулярным выражением
        match = re.search(
            r'DATEDIFF\(\s*TODAY\(\s*\)\s*,\s*\{([^}]+)\}\s*,\s*\'([^\']+)\'\s*\)',
            expr
        )
        
        if not match:
            return None
        
        field_name, unit = match.groups()
        start_date = await cls._parse_date(data.get(field_name))
        
        if not start_date:
            return None
        
        delta = relativedelta(date.today(), start_date)
        
        # Формируем результат на основе unit
        results = {
            'years': delta.years,
            'months': delta.years * 12 + delta.months,
            'days': (date.today() - start_date).days,
            'full': cls._format_full_stage(delta)
        }
        
        return results.get(unit)
    
    @staticmethod
    def _format_full_stage(delta: relativedelta) -> str:
        """Форматирование полного стажа"""
        parts = []
        if delta.years:
            parts.append(f"{delta.years} г.")
        if delta.months:
            parts.append(f"{delta.months} мес.")
        if delta.days:
            parts.append(f"{delta.days} дн.")
        return " ".join(parts) if parts else "0 дн."
    
    @classmethod
    async def _handle_concat(cls, expr: str, data: Dict[str, Any]) -> Optional[str]:
        """Оптимизированная конкатенация"""
        # Убираем CONCAT() и разбиваем по запятым
        content = expr[7:-1]  # вырезаем CONCAT( и )
        
        result = []
        buffer = []
        in_quotes = False
        quote_char = None
        
        # Ручной парсинг с учетом кавычек
        for char in content:
            if char in ('"', "'") and (not buffer or buffer[-1] != '\\'):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                elif char == quote_char:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                result.append(''.join(buffer).strip())
                buffer = []
            else:
                buffer.append(char)
        
        if buffer:
            result.append(''.join(buffer).strip())
        
        # Собираем результат
        output = []
        for arg in result:
            if arg.startswith(('"', "'")) and arg.endswith(('"', "'")):
                output.append(arg[1:-1])
            elif arg.startswith('{') and arg.endswith('}'):
                field_name = arg[1:-1]
                output.append(str(data.get(field_name, '')))
            else:
                output.append(arg)
        
        return ''.join(output)
    
    @classmethod
    async def _handle_arithmetic(cls, formula: str, data: Dict[str, Any]) -> Optional[Union[float, int]]:
        """Безопасное вычисление арифметики"""
        # Заменяем поля
        expr = formula
        for field_name in re.findall(r'\{([^}]+)\}', formula):
            value = data.get(field_name)
            if value is None:
                return None
            expr = expr.replace(
                f'{{{field_name}}}', 
                f'"{value}"' if isinstance(value, str) else str(value)
            )
        
        # Безопасный eval с ограниченными возможностями
        try:
            allowed_names = {
                'abs': abs, 'round': round, 'int': int, 'float': float
            }
            return eval(expr, {"__builtins__": {}}, allowed_names)
        except Exception as e:
            logger.error(f"Arithmetic error: {e}")
            return None