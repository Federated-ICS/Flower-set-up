# Quick Start Guide

## Setup (First Time)

### 1. Start PostgreSQL
```bash
# Option A: Use the setup script
chmod +x scripts/setup_postgres.sh
./scripts/setup_postgres.sh

# Option B: Manual setup
docker-compose up -d postgres
sleep 5
poetry run alembic upgrade head
```

### 2. Seed Database
```bash
poetry run python scripts/seed_database.py
```

### 3. Test Repositories
```bash
poetry run python scripts/test_repositories.py
```

### 4. Start Backend
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

### 5. Visit API Docs
Open: http://localhost:8000/docs

---

## Daily Development

```bash
# Terminal 1: Start PostgreSQL (if not running)
docker-compose up postgres

# Terminal 2: Start backend
poetry run uvicorn app.main:app --reload --port 8000

# Terminal 3: Start frontend (in webapp directory)
cd ../webapp
pnpm dev
```

---

## Useful Commands

### Database
```bash
# Run migrations
poetry run alembic upgrade head

# Create new migration
poetry run alembic revision --autogenerate -m "Description"

# Rollback migration
poetry run alembic downgrade -1

# Reset database (⚠️ deletes all data)
rm ics_threat_detection.db  # if using SQLite
docker-compose down -v postgres  # if using PostgreSQL
poetry run alembic upgrade head
poetry run python scripts/seed_database.py
```

### Docker
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d postgres redis

# Stop all
docker-compose down

# View logs
docker-compose logs -f postgres

# Check status
docker-compose ps
```

### Testing
```bash
# Test repositories
poetry run python scripts/test_repositories.py

# Run pytest (when tests are added)
poetry run pytest

# With coverage
poetry run pytest --cov=app tests/
```

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # ✅ FastAPI app
│   ├── config.py            # ✅ Settings
│   ├── database.py          # ✅ DB connection
│   ├── models/              # ✅ SQLAlchemy models
│   ├── schemas/             # ✅ Pydantic schemas
│   ├── repositories/        # ✅ Data access layer
│   ├── api/                 # ⏳ API routes (next)
│   ├── services/            # ⏳ Business logic (next)
│   └── utils/               # ⏳ Utilities (next)
├── scripts/
│   ├── seed_database.py     # ✅ Seed mock data
│   ├── test_repositories.py # ✅ Test repos
│   └── setup_postgres.sh    # ✅ Setup script
├── alembic/                 # ✅ Migrations
├── docker-compose.yml       # ✅ Infrastructure
└── pyproject.toml           # ✅ Dependencies
```

---

## What's Working

✅ **Database**: PostgreSQL with async SQLAlchemy
✅ **Models**: All tables created (alerts, FL rounds, predictions)
✅ **Repositories**: Full CRUD operations with filtering
✅ **Seed Data**: 20 alerts, 4 FL rounds, 10 predictions
✅ **API Server**: Running on http://localhost:8000

---

## What's Next

⏳ **API Endpoints**: Create routes for alerts, FL, predictions
⏳ **WebSocket**: Real-time updates
⏳ **Services**: Business logic layer
⏳ **Frontend Integration**: Connect React app

---

## Troubleshooting

### Port 8000 already in use
```bash
lsof -i :8000
kill -9 <PID>
```

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Migration error
```bash
# Check current version
poetry run alembic current

# Reset migrations (⚠️ deletes data)
poetry run alembic downgrade base
poetry run alembic upgrade head
```

---

## Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# Database
DATABASE_URL=postgresql+asyncpg://ics_user:ics_password@localhost:5432/ics_threat_detection

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j_password

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

---

**Last Updated**: November 10, 2025
