.PHONY: install dev test lint format typecheck check run docker

install:
	uv sync

dev:
	uv run fastapi dev app/main.py

run:
	uv run fastapi run app/main.py --host 0.0.0.0 --port 8000

test:
	uv run pytest --cov

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy

check: lint typecheck test

docker:
	docker build -t andi1984-api .
