.PHONY: help install install-dev lint test migrate db-shell run clean

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PIP_SYNC = $(VENV)/bin/pip-sync
UVICORN = $(VENV)/bin/uvicorn
RUFF = $(VENV)/bin/ruff
MYPY = $(VENV)/bin/mypy
PYTEST = $(VENV)/bin/pytest
ALEMBIC = $(VENV)/bin/alembic

help:
	@echo "Commands:"
	@echo "  install       Установить prod зависимости"
	@echo "  install-dev   Установить dev зависимости"
	@echo "  lint          Запустить ruff и mypy"
	@echo "  test          Запустить тесты"
	@echo "  migrate       Применить миграции"
	@echo "  db-shell      Подключиться к БД"
	@echo "  run           Запустить dev сервер"
	@echo "  clean         Очистить кэш Python"

install:
	$(PIP_SYNC) requirements/base.txt

install-dev:
	$(PIP_SYNC) requirements/dev.txt

lint:
	$(RUFF) check src/
	$(MYPY) src/

test:
	$(PYTEST) tests/ -v --cov=src/app

migrate:
	$(ALEMBIC) upgrade head

db-shell:
	docker exec -it table-saas-db psql -U postgres -d table_saas

run:
	$(UVICORN) src.app.main:app --reload

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete