.PHONY: lint mypy check

init-dev:
	pipx install poetry
lint:
	poetry run black .
	poetry run ruff check complex.py

mypy:
	poetry run mypy complex.py
	poetry run mypy src

check: lint mypy
	@echo "✅ Проверки пройдены"