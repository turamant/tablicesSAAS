#!/bin/bash

# Создаем проект
mkdir -p table-saas-backend
cd table-saas-backend

# Создаем структуру папок
mkdir -p src/app/{core,models,schemas,api/v1,services,utils,middleware}
mkdir -p tests/{test_api,test_services}
mkdir -p requirements alembic/versions scripts

# Создаем пустые __init__.py файлы
touch src/app/__init__.py
touch src/app/core/__init__.py
touch src/app/models/__init__.py
touch src/app/schemas/__init__.py
touch src/app/api/__init__.py
touch src/app/api/v1/__init__.py
touch src/app/services/__init__.py
touch src/app/utils/__init__.py
touch src/app/middleware/__init__.py
touch tests/__init__.py
touch tests/conftest.py

# Создаем основные файлы
touch src/app/main.py
touch src/app/core/config.py
touch src/app/core/security.py
touch src/app/core/database.py
touch src/app/core/exceptions.py
touch src/app/models/base.py
touch src/app/models/user.py
touch src/app/models/table.py
touch src/app/models/field.py
touch src/app/models/refresh_token.py
touch src/app/schemas/user.py
touch src/app/schemas/table.py
touch src/app/schemas/field.py
touch src/app/schemas/auth.py
touch src/app/api/dependencies.py
touch src/app/api/v1/auth.py
touch src/app/api/v1/tables.py
touch src/app/api/v1/fields.py
touch src/app/api/v1/data.py
touch src/app/services/auth_service.py
touch src/app/services/table_service.py
touch src/app/services/data_service.py
touch src/app/utils/validators.py
touch src/app/middleware/auth_middleware.py
touch scripts/seed_db.py
touch scripts/cleanup.py
touch .env .env.example
touch .gitignore
touch pyproject.toml
touch setup.cfg
touch docker-compose.yml
touch Dockerfile
touch Makefile
touch README.md

# Создаем requirements файлы
cat > requirements/base.in << 'EOF'
# Ядро
fastapi[all]>=0.115.0
uvicorn[standard]>=0.30.0

# База данных
asyncpg>=0.30.0
sqlalchemy>=2.0.0
alembic>=1.13.0
psycopg2-binary>=2.9.0

# Безопасность
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.9

# Валидация
pydantic[email]>=2.0.0
pydantic-settings>=2.0.0

# Утилиты
python-dotenv>=1.0.0
EOF

cat > requirements/dev.in << 'EOF'
-c base.txt

# Тестирование
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=5.0.0
httpx>=0.27.0
factory-boy>=3.3.0

# Линтеры и форматтеры
ruff>=0.3.0
mypy>=1.8.0
pre-commit>=3.6.0

# Утилиты разработки
ipython>=8.20.0
watchdog>=4.0.0
EOF

# Создаем .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/
.env
.venv
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project
alembic/versions/*.pyc
*.db
*.sqlite3

# Logs
*.log
EOF

# Создаем .env.example
cat > .env.example << 'EOF'
# БД
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=table_saas

# Безопасность
SECRET_KEY=super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Режим
DEBUG=True
ENVIRONMENT=development
EOF

# Создаем docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: table-saas-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: table_saas
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# Создаем Makefile
cat > Makefile << 'EOF'
.PHONY: help install dev lint test migrate db-shell

help:
	@echo "Commands:"
	@echo "  install     Установить prod зависимости"
	@echo "  dev         Установить dev зависимости"
	@echo "  lint        Запустить ruff и mypy"
	@echo "  test        Запустить тесты"
	@echo "  migrate     Применить миграции"
	@echo "  db-shell    Подключиться к БД"

install:
	pip-sync requirements/base.txt

dev:
	pip-sync requirements/dev.txt

lint:
	ruff check src/
	mypy src/

test:
	pytest tests/ -v --cov=src/app

migrate:
	alembic upgrade head

db-shell:
	docker exec -it table-saas-db psql -U postgres -d table_saas
EOF

# Создаем pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "table-saas-backend"
version = "0.1.0"
description = "SaaS конструктор таблиц"
authors = [{name = "Your Name"}]

[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_interface"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true
EOF

# Создаем базовый main.py
cat > src/app/main.py << 'EOF'
from fastapi import FastAPI

app = FastAPI(title="Table SaaS", version="0.1.0")

@app.get("/")
async def root():
    return {"message": "Table SaaS API"}
EOF

# Создаем базовый config.py
cat > src/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "table_saas"
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

settings = Settings()
EOF

echo "✅ Структура проекта создана!"
echo "📁 cd table-saas-backend"
echo "🐍 pyenv local 3.12.9"
echo "🔧 python -m venv venv"
echo "🔄 source venv/bin/activate"
echo "📦 pip install pip-tools"
echo "⚙️ pip-compile requirements/base.in -o requirements/base.txt"
echo "⚙️ pip-compile requirements/dev.in -o requirements/dev.txt"
echo "📦 pip-sync requirements/dev.txt"
echo "🐳 docker-compose up -d"
echo "🚀 uvicorn src.app.main:app --reload"