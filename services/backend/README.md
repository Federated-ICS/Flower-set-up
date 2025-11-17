# ICS Threat Detection System - Backend

[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml)
[![Quick Check](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quick-check.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/quick-check.yml)
[![Security Scan](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/security.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO/branch/master/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/YOUR_REPO)

FastAPI backend for the Federated Network-Based ICS Threat Detection System. A multi-layered threat detection platform using federated learning, LSTM autoencoders, and graph neural networks to detect and predict ICS/OT network attacks.

## Overview

This system provides real-time threat detection and prediction for Industrial Control Systems (ICS) and Operational Technology (OT) networks using a three-layer detection architecture:

**Layer 1: Anomaly Detection**
- LSTM Autoencoder for temporal pattern analysis (60-second context windows)
- Isolation Forest for statistical anomaly detection

**Layer 2: Threat Classification**
- Multi-class classifier for MITRE ATT&CK technique identification
- Context-aware analysis using Redis buffer

**Layer 3: Attack Prediction**
- Graph Neural Network (GNN) for predicting next attack steps
- Neo4j-based MITRE ATT&CK knowledge graph

**Federated Learning**
- Privacy-preserving model training across multiple facilities
- Differential privacy with ε=0.5, δ=10⁻⁵
- Secure aggregation without sharing raw data

## Quick Start

```bash
# 1. Install dependencies (using Poetry)
make install
# or: poetry install

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 3. Start PostgreSQL
make docker-up
# or: docker-compose up -d postgres

# 4. Run database migrations
make migrate
# or: poetry run alembic upgrade head

# 5. Seed database with sample data
make seed
# or: poetry run python scripts/seed_database.py

# 6. Start the server
make dev
# or: poetry run uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/docs for interactive API documentation.

### Using Makefile Commands

```bash
make help          # Show all available commands
make ci            # Run all CI checks locally
make test          # Run tests
make format        # Format code
make lint          # Check code quality
```

## Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get up and running fast
- [CI/CD Setup](docs/CI_SETUP.md) - Configure GitHub Actions pipeline
- [CI/CD Documentation](docs/CI_CD.md) - Detailed CI/CD information
- [Architecture](docs/ARCHITECTURE.md) - System design and data flows
- [Progress](docs/PROGRESS.md) - Implementation status
- [TDD Status](docs/TDD_STATUS.md) - Test-driven development progress

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management (Pydantic Settings)
│   ├── database.py          # Async SQLAlchemy setup
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── alert.py         # Alert and AlertSource models
│   │   ├── fl_round.py      # FLRound and FLClient models
│   │   ├── prediction.py    # Prediction and PredictedTechnique models
│   │   └── network_data.py  # NetworkData model
│   ├── schemas/             # Pydantic validation schemas
│   │   ├── alert.py
│   │   ├── fl_status.py
│   │   └── prediction.py
│   ├── repositories/        # Data access layer
│   │   ├── alert_repository.py
│   │   ├── fl_repository.py
│   │   └── prediction_repository.py
│   └── api/                 # API route handlers
│       ├── alerts.py        # Alert management endpoints
│       ├── fl_status.py     # Federated learning endpoints
│       └── predictions.py   # Attack prediction endpoints
├── scripts/                 # Utility scripts
│   ├── seed_database.py     # Populate with sample data
│   ├── test_repositories.py # Test data access layer
│   ├── clear_database.py    # Reset database
│   └── setup_postgres.sh    # PostgreSQL setup script
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest fixtures
│   └── test_api/            # API endpoint tests
├── alembic/                 # Database migrations
│   └── versions/            # Migration files
├── docs/                    # Documentation
├── pyproject.toml           # Poetry dependencies
├── docker-compose.yml       # Infrastructure services
└── .env.example            # Environment variables template
```

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - System health status

### Alerts (`/api/alerts`)
- `GET /api/alerts` - List alerts with filtering and pagination
  - Query params: `severity`, `facility`, `status_filter`, `search`, `time_range`, `page`, `limit`
- `POST /api/alerts` - Create new alert
- `GET /api/alerts/stats` - Get alert statistics
- `GET /api/alerts/{id}` - Get alert by ID
- `PUT /api/alerts/{id}/status` - Update alert status

### Federated Learning (`/api/fl`)
- `GET /api/fl/rounds/current` - Get current active FL round
- `POST /api/fl/rounds/trigger` - Start new FL round
- `GET /api/fl/rounds` - List all FL rounds
- `GET /api/fl/rounds/{id}` - Get FL round by ID
- `PUT /api/fl/rounds/{id}/progress` - Update round progress
- `POST /api/fl/rounds/{id}/complete` - Complete FL round
- `GET /api/fl/clients` - List all FL clients
- `GET /api/fl/clients/{id}` - Get FL client by ID
- `PUT /api/fl/clients/{id}` - Update client status
- `GET /api/fl/privacy-metrics` - Get privacy metrics

### Attack Predictions (`/api/predictions`)
- `GET /api/predictions` - List predictions with filtering
  - Query params: `limit`, `offset`, `validated`
- `POST /api/predictions` - Create new prediction
- `GET /api/predictions/latest` - Get most recent prediction
- `GET /api/predictions/{id}` - Get prediction by ID
- `POST /api/predictions/{id}/validate` - Mark prediction as validated

Interactive API documentation available at http://localhost:8000/docs

## Development

### Running Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app tests/

# Run specific test file
poetry run pytest tests/test_api/test_alerts.py -v

# Run API tests
poetry run pytest tests/test_api/ -v
```

### Database Management
```bash
# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# Seed database with sample data
poetry run python scripts/seed_database.py

# Clear database
poetry run python scripts/clear_database.py

# Test repositories
poetry run python scripts/test_repositories.py
```

### Code Quality
```bash
# Format code
poetry run black app/
poetry run isort app/

# Type checking
poetry run mypy app/

# Linting
poetry run flake8 app/
```

### Docker Services
```bash
# Start all infrastructure services
docker-compose up -d

# Start specific service
docker-compose up -d postgres redis

# View logs
docker-compose logs -f postgres

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

## Tech Stack

### Core Framework
- **FastAPI** 0.104+ - Modern async web framework with automatic OpenAPI docs
- **Python** 3.11+ - Type hints and async/await support
- **Poetry** - Dependency management and packaging

### Database & ORM
- **PostgreSQL** 15 - Primary relational database
- **SQLAlchemy** 2.0+ - Async ORM with declarative models
- **Alembic** - Database migrations
- **asyncpg** - High-performance async PostgreSQL driver

### Data Validation
- **Pydantic** 2.5+ - Data validation and settings management
- **Pydantic Settings** - Environment variable management

### Infrastructure Services
- **Redis** 7 - Context buffer for 60-second rolling windows
- **Apache Kafka** - Event streaming and message bus
- **Neo4j** 5.14 - Graph database for MITRE ATT&CK relationships
- **Zookeeper** - Kafka coordination

### Development Tools
- **pytest** - Testing framework with async support
- **pytest-asyncio** - Async test support
- **httpx** - Async HTTP client for testing
- **black** - Code formatting
- **isort** - Import sorting
- **mypy** - Static type checking
- **flake8** - Linting

## Features

✅ **Implemented**
- RESTful API with FastAPI
- Async database operations with SQLAlchemy
- Repository pattern for data access
- Alert management with filtering and search
- Federated learning round tracking
- Attack prediction storage
- Database migrations with Alembic
- Comprehensive test suite
- Docker Compose infrastructure
- Sample data seeding

🚧 **In Progress**
- WebSocket support for real-time updates
- Kafka consumer integration
- Redis context buffer service
- Neo4j graph queries

📋 **Planned**
- Authentication and authorization
- Rate limiting
- Caching layer
- Background task processing
- Monitoring and logging
- Production deployment configs

## Environment Variables

Create a `.env` file from `.env.example`:

```bash
cp .env.example .env
```

Key configuration options:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection

# Redis (Context Buffer)
REDIS_URL=redis://localhost:6379/0

# Kafka (Event Streaming)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Neo4j (MITRE ATT&CK Graph)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# CORS (Frontend URLs)
CORS_ORIGINS=["http://localhost:3000"]

# Security
SECRET_KEY=your-secret-key-change-in-production

# Demo Mode
DEMO_MODE=true
SEED_DATA_ON_STARTUP=false
```

## Troubleshooting

### Port 8000 already in use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Migration errors
```bash
# Check current migration version
poetry run alembic current

# Reset database (⚠️ deletes all data)
docker-compose down -v postgres
docker-compose up -d postgres
sleep 5
poetry run alembic upgrade head
poetry run python scripts/seed_database.py
```

### Poetry dependency issues
```bash
# Clear cache and reinstall
poetry cache clear pypi --all
poetry install --no-cache
```

## CI/CD Pipeline

This project uses GitHub Actions for continuous integration and deployment:

### Workflows

**CI Pipeline** (`.github/workflows/ci.yml`)
- Runs on every push and pull request
- Executes full test suite with coverage reporting
- Runs linting (Black, isort, flake8)
- Performs type checking with mypy
- Uploads coverage to Codecov

**Quick Check** (`.github/workflows/quick-check.yml`)
- Fast feedback for API tests
- Runs on every push and pull request
- Focuses on API endpoint tests

**Security Scan** (`.github/workflows/security.yml`)
- Dependency vulnerability scanning
- Code security analysis with Bandit
- Runs on push, PR, and weekly schedule

### Running CI Locally

```bash
# Run all tests like CI does
poetry run pytest tests/ -v --cov=app --cov-report=term

# Check code formatting
poetry run black --check app/ tests/
poetry run isort --check-only app/ tests/
poetry run flake8 app/ tests/ --max-line-length=100

# Type checking
poetry run mypy app/ --ignore-missing-imports
```

## Contributing

This project follows Test-Driven Development (TDD). See [TDD_STATUS.md](docs/TDD_STATUS.md) for current test coverage and implementation status.

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Ensure all tests pass locally
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

All PRs must pass CI checks before merging.

## License

[Your License Here]
