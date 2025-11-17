.PHONY: help install test test-api test-cov lint format type-check security clean docker-up docker-down migrate seed

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies with Poetry"
	@echo "  make test          - Run all tests"
	@echo "  make test-api      - Run API tests only"
	@echo "  make test-cov      - Run tests with coverage report"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with Black and isort"
	@echo "  make type-check    - Run mypy type checking"
	@echo "  make security      - Run security scans"
	@echo "  make ci            - Run all CI checks locally"
	@echo "  make clean         - Clean up cache and temp files"
	@echo "  make docker-up     - Start Docker services"
	@echo "  make docker-down   - Stop Docker services"
	@echo "  make migrate       - Run database migrations"
	@echo "  make seed          - Seed database with sample data"
	@echo "  make dev           - Start development server"
	@echo "  make pre-commit    - Install pre-commit hooks"

install:
	poetry install

test:
	poetry run pytest tests/ -v

test-api:
	poetry run pytest tests/test_api/ -v

test-cov:
	poetry run pytest tests/ -v --cov=app --cov-report=xml --cov-report=term --cov-report=html

lint:
	poetry run black --check app/ tests/
	poetry run isort --check-only app/ tests/
	poetry run flake8 app/ tests/

format:
	poetry run black app/ tests/
	poetry run isort app/ tests/

type-check:
	poetry run mypy app/ --ignore-missing-imports

security:
	@echo "Running Bandit security scan..."
	@poetry run bandit -r app/ -f screen || true
	@echo "\nExporting requirements for Safety check..."
	@poetry export -f requirements.txt --output requirements.txt --without-hashes
	@echo "Note: Run 'safety check --file=requirements.txt' manually if you have Safety installed"

ci: format lint type-check test-cov
	@echo "\n✅ All CI checks passed!"

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -f coverage.xml requirements.txt bandit-report.json

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

migrate:
	poetry run alembic upgrade head

migrate-create:
	@read -p "Enter migration message: " msg; \
	poetry run alembic revision --autogenerate -m "$$msg"

seed:
	poetry run python scripts/seed_database.py

clear-db:
	poetry run python scripts/clear_database.py

dev:
	poetry run uvicorn app.main:app --reload --port 8000

pre-commit:
	poetry run pre-commit install
	@echo "✅ Pre-commit hooks installed!"

pre-commit-run:
	poetry run pre-commit run --all-files
