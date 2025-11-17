# Docker Setup Guide

## Quick Start

### 1. Start All Services

```bash
# Start all infrastructure services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 2. Verify Services

```bash
# PostgreSQL
docker exec -it ics-postgres psql -U ics_user -d ics_threat_detection -c "SELECT version();"

# Redis
docker exec -it ics-redis redis-cli ping

# Neo4j (visit in browser)
# http://localhost:7474
# Username: neo4j
# Password: neo4j_password

# Kafka
docker exec -it ics-kafka kafka-topics --list --bootstrap-server localhost:9092
```

### 3. Update .env File

```bash
# Copy example
cp .env.example .env

# Edit with your settings (already configured for Docker)
nano .env
```

### 4. Run Database Migrations

```bash
# With PostgreSQL running
poetry run alembic upgrade head
```

### 5. Start Backend

```bash
poetry run uvicorn app.main:app --reload --port 8000
```

---

## Services Overview

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| PostgreSQL | 5432 | Primary database | `docker exec ics-postgres pg_isready` |
| Redis | 6379 | Context buffer | `docker exec ics-redis redis-cli ping` |
| Neo4j | 7474, 7687 | MITRE ATT&CK graph | http://localhost:7474 |
| Zookeeper | 2181 | Kafka coordination | - |
| Kafka | 9092 | Event streaming | `docker exec ics-kafka kafka-broker-api-versions --bootstrap-server localhost:9092` |

---

## Common Commands

### Start/Stop Services

```bash
# Start all
docker-compose up -d

# Start specific service
docker-compose up -d postgres redis

# Stop all
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f kafka
```

### Access Services

```bash
# PostgreSQL shell
docker exec -it ics-postgres psql -U ics_user -d ics_threat_detection

# Redis CLI
docker exec -it ics-redis redis-cli

# Kafka shell
docker exec -it ics-kafka bash
```

### Create Kafka Topics

```bash
# Create topics for the system
docker exec -it ics-kafka kafka-topics --create \
  --topic network_data \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

docker exec -it ics-kafka kafka-topics --create \
  --topic alerts \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

docker exec -it ics-kafka kafka-topics --create \
  --topic predictions \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

docker exec -it ics-kafka kafka-topics --create \
  --topic fl_events \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1

# List topics
docker exec -it ics-kafka kafka-topics --list --bootstrap-server localhost:9092
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :5432  # PostgreSQL
sudo lsof -i :6379  # Redis
sudo lsof -i :9092  # Kafka

# Kill process
sudo kill -9 <PID>
```

### Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Restart service
docker-compose restart <service-name>

# Remove and recreate
docker-compose down
docker-compose up -d
```

### Reset Everything

```bash
# Stop and remove all containers and volumes
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

### Check Container Health

```bash
# All containers
docker-compose ps

# Specific container
docker inspect ics-postgres | grep -A 10 Health
```

---

## Development Workflow

### Option 1: Full Docker Stack (Recommended for Production-like)

```bash
# Terminal 1: Start infrastructure
docker-compose up

# Terminal 2: Start backend
poetry run uvicorn app.main:app --reload --port 8000

# Terminal 3: Start frontend
cd ../webapp
pnpm dev
```

### Option 2: Minimal Stack (Faster for Development)

```bash
# Only start what you need
docker-compose up -d postgres redis

# Use SQLite instead of PostgreSQL
# Edit .env: DATABASE_URL=sqlite+aiosqlite:///./ics_threat_detection.db

# Start backend
poetry run uvicorn app.main:app --reload --port 8000
```

### Option 3: No Docker (Fastest for Quick Testing)

```bash
# Use SQLite only
# Edit .env: DATABASE_URL=sqlite+aiosqlite:///./ics_threat_detection.db

# Start backend
poetry run uvicorn app.main:app --reload --port 8000

# Note: No Kafka, Redis, or Neo4j features will work
```

---

## Data Persistence

All data is stored in Docker volumes:
- `postgres_data` - Database tables
- `redis_data` - Context buffer
- `neo4j_data` - MITRE ATT&CK graph
- `kafka_data` - Event logs

To backup:
```bash
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

To restore:
```bash
docker run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

---

## Resource Usage

Approximate memory usage:
- PostgreSQL: ~50MB
- Redis: ~10MB
- Neo4j: ~500MB
- Kafka + Zookeeper: ~500MB

**Total: ~1GB RAM**

To limit resources, add to docker-compose.yml:
```yaml
services:
  postgres:
    deploy:
      resources:
        limits:
          memory: 256M
```

---

## Next Steps

1. ✅ Start Docker services: `docker-compose up -d`
2. ✅ Verify all healthy: `docker-compose ps`
3. ✅ Update .env file with PostgreSQL URL
4. ✅ Run migrations: `poetry run alembic upgrade head`
5. ✅ Start backend: `poetry run uvicorn app.main:app --reload`
6. ✅ Visit API docs: http://localhost:8000/docs

---

**Last Updated**: November 10, 2025
