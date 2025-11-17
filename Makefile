.PHONY: help install test lint format clean dev up down logs build restart ps

# Default target
help:
	@echo "FedICS - Federated ICS Security System"
	@echo ""
	@echo "Available commands:"
	@echo "  make install      - Install Python dependencies"
	@echo "  make test         - Run all tests"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Clean up temporary files and caches"
	@echo ""
	@echo "Docker commands:"
	@echo "  make dev          - Start all services in development mode (hot reload)"
	@echo "  make up           - Start all services in production mode"
	@echo "  make down         - Stop all services"
	@echo "  make build        - Build all Docker images"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - Follow logs from all services"
	@echo "  make ps           - Show running containers"
	@echo ""
	@echo "Database commands:"
	@echo "  make migrate      - Run database migrations"
	@echo "  make db-reset     - Reset database (WARNING: deletes all data)"
	@echo "  make db-seed      - Seed database with sample data"
	@echo ""
	@echo "Kafka commands:"
	@echo "  make kafka-topics - List all Kafka topics"
	@echo "  make kafka-clear  - Delete all Kafka topics (reset)"
	@echo ""
	@echo "Service-specific:"
	@echo "  make backend      - Start only backend service"
	@echo "  make dashboard    - Start only dashboard service"
	@echo "  make fl           - Start only FL services (server + clients)"

# Installation
install:
	pip install -r requirements.txt
	@echo "✓ Dependencies installed"

# Testing
test:
	pytest test_setup.py -v

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

# Code quality
lint:
	ruff check src/ services/
	mypy src/

format:
	black src/ services/ tests/
	isort src/ services/ tests/
	@echo "✓ Code formatted"

# Cleanup
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
	@echo "✓ Cleaned up temporary files"

# Docker Compose - Development
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-down:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down

# Docker Compose - Production
up:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

down-volumes:
	docker compose down -v
	@echo "⚠️  All volumes deleted"

build:
	docker compose build

rebuild:
	docker compose build --no-cache

restart:
	docker compose restart

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f fastapi-backend

logs-dashboard:
	docker compose logs -f dashboard

logs-fl:
	docker compose logs -f flower-server fl-client-0 fl-client-1 fl-client-2

ps:
	docker compose ps

# Service-specific commands
backend:
	docker compose up -d postgres redis neo4j kafka fastapi-backend

dashboard:
	docker compose up -d fastapi-backend dashboard

fl:
	docker compose up -d kafka flower-server fl-client-0 fl-client-1 fl-client-2

detectors:
	docker compose up -d kafka network-simulator anomaly-lstm anomaly-iforest anomaly-physics threat-classifier severity-predictor

# Database commands
migrate:
	cd services/backend && poetry run alembic upgrade head
	@echo "✓ Migrations applied"

db-reset:
	docker compose down postgres
	docker volume rm flower-set-up_pgdata 2>/dev/null || true
	docker compose up -d postgres
	sleep 5
	$(MAKE) migrate
	@echo "✓ Database reset complete"

db-seed:
	cd services/backend && poetry run python scripts/seed_database.py
	@echo "✓ Database seeded"

db-shell:
	docker compose exec postgres psql -U postgres -d ics_threat_detection

# Kafka commands
kafka-topics:
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

kafka-clear:
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic network_data || true
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic anomalies || true
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic attack_classified || true
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic attack_predicted || true
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic alerts || true
	docker compose exec kafka kafka-topics --bootstrap-server localhost:9092 --delete --topic fl_events || true
	@echo "✓ Kafka topics cleared"

kafka-consumer:
	docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic $(TOPIC) --from-beginning

# Health checks
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health || echo "❌ Backend not responding"
	@curl -s http://localhost:3000 > /dev/null && echo "✓ Dashboard running" || echo "❌ Dashboard not responding"
	@docker compose exec postgres pg_isready -U postgres && echo "✓ PostgreSQL running" || echo "❌ PostgreSQL not responding"
	@docker compose exec redis redis-cli ping | grep -q PONG && echo "✓ Redis running" || echo "❌ Redis not responding"

# Setup for first-time users
setup:
	@echo "Setting up FedICS for the first time..."
	@test -f .env || (cp .env.example .env && echo "✓ Created .env file")
	$(MAKE) install
	$(MAKE) up-build
	@echo "Waiting for services to start..."
	@sleep 10
	$(MAKE) migrate
	$(MAKE) db-seed
	@echo ""
	@echo "✓ Setup complete!"
	@echo ""
	@echo "Services running at:"
	@echo "  - Dashboard:   http://localhost:3000"
	@echo "  - Backend API: http://localhost:8000/docs"
	@echo "  - Neo4j:       http://localhost:7474"
	@echo ""
	@echo "Run 'make help' for more commands"

# Quick development workflow
quick-dev:
	$(MAKE) dev-down
	$(MAKE) dev-build

# CI simulation
ci:
	$(MAKE) lint
	$(MAKE) test
	@echo "✓ CI checks passed"
