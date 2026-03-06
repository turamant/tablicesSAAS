from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import SQLModel
from src.app.models import *

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

print("="*50)
print("TABLES IN METADATA:", list(SQLModel.metadata.tables.keys()))
print("="*50)

target_metadata = SQLModel.metadata

# Функция для игнорирования динамических таблиц
def include_object(object, name, type_, reflected, compare_to):
    # Не трогаем динамические таблицы (data_*)
    if type_ == "table" and name.startswith("data_"):
        return False
    return True

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,  # Добавили сюда тоже
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            include_object=include_object,  # ← Вот здесь главное!
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()