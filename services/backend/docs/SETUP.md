# Backend Setup Guide

## Prerequisites

Before starting, ensure you have:
- Python 3.11+ installed
- Poetry installed (https://python-poetry.org/docs/#installation)
- PostgreSQL 15+ installed and running
- Redis 7.0+ installed and running
- Neo4j 5.x installed and running (optional for Phase 1)
- Kafka 3.6+ installed and running (optional for Phase 1)

### Install Poetry (if not installed)

**On Linux/Mac/WSL:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**On Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Verify Installation:**
```bash
poetry --version
```

---

## Phase 1: Basic FastAPI Setup

### Step 1: Navigate to Backend Directory

```bash
cd backend
```

### Step 2: Install Dependencies with Poetry

```bash
# Install all dependencies (including dev dependencies)
poetry install

# Or install only production dependencies
poetry install --no-dev
```

Poetry will automatically:
- Create a virtual environment
- Install all dependencies
- Lock dependency versions in poetry.lock

### Step 3: Activate Poetry Shell

```bash
poetry shell
```

This activates the virtual environment. Alternatively, you can run commands with `poetry run`:
```bash
poetry run uvicorn app.main:app --reload
```

### Step 4: Create Environment File

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials:
```bash
nano .env  # or use your preferred editor
```

### Step 5: Initialize Database

**Create PostgreSQL Database:**
```bash
# Login to PostgreSQL
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE ics_threat_detection;
CREATE USER ics_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ics_threat_detection TO ics_user;
\q
```

**Run Database Migrations:**
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### Step 6: Load Seed Data (Mock Data)

```bash
python scripts/seed_database.py
```

### Step 7: Start FastAPI Server

**Option 1: Inside Poetry Shell**
```bash
poetry shell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Option 2: Using Poetry Run**
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 8: Verify Installation

Open your browser and visit:
- API Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## Phase 2: Redis Setup (Context Buffer)

### Step 1: Install Redis (if not installed)

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
```

**On Mac (using Homebrew):**
```bash
brew install redis
```

**On Windows:**
Download from: https://redis.io/download

### Step 2: Start Redis Server

**On Linux/Mac:**
```bash
redis-server
```

**Or as a service:**
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

### Step 3: Verify Redis Connection

```bash
redis-cli ping
# Should return: PONG
```

### Step 4: Test Context Buffer

```bash
poetry run python scripts/test_redis_connection.py
```

---

## Phase 3: Kafka Setup (Event Streaming)

### Step 1: Install Kafka (if not installed)

**Using Docker (Recommended):**
```bash
# Create docker-compose.yml for Kafka
docker-compose up -d kafka zookeeper
```

**Manual Installation:**
Download from: https://kafka.apache.org/downloads

### Step 2: Start Kafka

**With Docker:**
```bash
docker-compose up -d
```

**Manual:**
```bash
# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Start Kafka (in another terminal)
bin/kafka-server-start.sh config/server.properties
```

### Step 3: Create Kafka Topics

```bash
# Create topics for the system
kafka-topics.sh --create --topic network_data --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics.sh --create --topic alerts --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics.sh --create --topic predictions --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics.sh --create --topic fl_events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
```

### Step 4: Verify Kafka Topics

```bash
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Step 5: Test Kafka Connection

```bash
poetry run python scripts/test_kafka_connection.py
```

---

## Phase 4: Neo4j Setup (MITRE ATT&CK Graph)

### Step 1: Install Neo4j (if not installed)

**Using Docker (Recommended):**
```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  neo4j:5.14
```

**Manual Installation:**
Download from: https://neo4j.com/download/

### Step 2: Access Neo4j Browser

Open: http://localhost:7474

Login with:
- Username: neo4j
- Password: your_password (set in docker command or during installation)

### Step 3: Load MITRE ATT&CK Data

```bash
poetry run python scripts/load_mitre_attack.py
```

### Step 4: Verify Graph Data

In Neo4j Browser, run:
```cypher
MATCH (n:Technique) RETURN count(n);
```

---

## Phase 5: Run Complete System

### Step 1: Start All Services

**Terminal 1 - PostgreSQL:**
```bash
# Should already be running as a service
sudo systemctl status postgresql
```

**Terminal 2 - Redis:**
```bash
redis-server
```

**Terminal 3 - Kafka (if using Docker):**
```bash
docker-compose up
```

**Terminal 4 - Neo4j (if using Docker):**
```bash
docker start neo4j
```

**Terminal 5 - FastAPI Backend:**
```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 6 - Kafka Consumer (WebSocket Bridge):**
```bash
cd backend
poetry run python app/services/kafka_consumer.py
```

**Terminal 7 - Frontend (in another terminal):**
```bash
cd webapp
pnpm dev
```

### Step 2: Verify All Services

Run the health check script:
```bash
poetry run python scripts/check_services.py
```

Expected output:
```
✓ FastAPI: Running on http://localhost:8000
✓ PostgreSQL: Connected
✓ Redis: Connected
✓ Kafka: Connected
✓ Neo4j: Connected
✓ Frontend: Running on http://localhost:3000
```

---

## Development Workflow

### Daily Startup

```bash
# 1. Activate virtual environment
cd backend
source venv/bin/activate

# 2. Start backend
uvicorn app.main:app --reload --port 8000

# 3. In another terminal, start frontend
cd webapp
pnpm dev
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py
```

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### View Logs

```bash
# FastAPI logs (in terminal where uvicorn is running)

# Kafka logs
docker-compose logs -f kafka

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Redis logs
redis-cli monitor
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check connection
psql -U ics_user -d ics_threat_detection -h localhost
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Restart Redis
sudo systemctl restart redis
```

### Kafka Connection Error

```bash
# Check Kafka is running
docker-compose ps

# Restart Kafka
docker-compose restart kafka

# View Kafka logs
docker-compose logs kafka
```

### Module Not Found Error

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install <package-name>
```

---

## Quick Reference

### Useful Commands

```bash
# Check Python version
python --version

# List installed packages
pip list

# Check FastAPI routes
python -c "from app.main import app; print(app.routes)"

# Test API endpoint
curl http://localhost:8000/health

# Check database tables
psql -U ics_user -d ics_threat_detection -c "\dt"

# Monitor Redis
redis-cli monitor

# List Kafka topics
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### Environment Variables Reference

```bash
# Database
DATABASE_URL=postgresql://ics_user:password@localhost:5432/ics_threat_detection

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# API
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000

# Security
SECRET_KEY=your-secret-key-here
```

---

## Next Steps

After completing setup:

1. ✅ Verify all services are running
2. ✅ Check API documentation at http://localhost:8000/docs
3. ✅ Test health endpoint: http://localhost:8000/health
4. ✅ Verify database has seed data
5. ✅ Test WebSocket connection
6. ✅ Connect frontend to backend

Then proceed to:
- Implement detection models integration
- Add Federated Learning endpoints
- Implement attack prediction API
- Build demo scenarios

---

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review logs for error messages
3. Verify all services are running
4. Check environment variables are set correctly

---

**Setup Version:** 1.0  
**Last Updated:** November 10, 2025  
**Target Demo Date:** November 30, 2025
