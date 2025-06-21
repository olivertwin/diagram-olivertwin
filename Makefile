.PHONY: lint mypy check init-dev init

init:
	pip install poetry
	poetry install --without dev
init-dev: init
	poetry install --with dev

lint:
	poetry run black --check .
	poetry run ruff check complex.py

mypy:
	poetry run mypy complex.py
	poetry run mypy src

build: init
	poetry build

check: lint mypy
	@echo "✅ Проверки пройдены"