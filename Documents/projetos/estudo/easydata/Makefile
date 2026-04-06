.PHONY: help install dev-install test lint format clean docker-up docker-down migrate seed

help:
	@echo "Trivaxion - Makefile Commands"
	@echo ""
	@echo "install          Install production dependencies"
	@echo "dev-install      Install development dependencies"
	@echo "test             Run tests"
	@echo "test-cov         Run tests with coverage"
	@echo "lint             Run linters"
	@echo "format           Format code"
	@echo "clean            Clean build artifacts"
	@echo "docker-up        Start Docker services"
	@echo "docker-down      Stop Docker services"
	@echo "migrate          Run database migrations"
	@echo "seed             Seed initial data"
	@echo "indices          Create Elasticsearch indices"

install:
	pip install uv
	uv pip install --system -r pyproject.toml
	uv pip install --system -e .

dev-install:
	pip install uv
	uv pip install --system -r pyproject.toml
	uv pip install --system -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=src/trivaxion --cov-report=html --cov-report=term

lint:
	ruff check src/
	mypy src/ --ignore-missing-imports

format:
	ruff format src/
	ruff check --fix src/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/

docker-up:
	docker-compose -f docker-compose.local.yml up -d

docker-down:
	docker-compose -f docker-compose.local.yml down

migrate:
	alembic upgrade head

seed:
	docker-compose -f docker-compose.local.yml exec app python scripts/seed/initial_data.py

indices:
	python scripts/bootstrap/create_indices.py

run:
	uvicorn trivaxion.main:app --reload --host 0.0.0.0 --port 8000
