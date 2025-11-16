# Backend Implementation Steps

## Overview

This document outlines the step-by-step implementation plan for the FastAPI backend, from initial setup to full integration with the webapp.

---

## Phase 1: Foundation Setup (Day 1-2)

### Step 1: Project Initialization
**Goal**: Set up basic project structure

**Tasks**:
1. ✅ Create directory structure
2. ✅ Initialize Poetry project (already done)
3. ✅ Create all necessary folders
4. ✅ Set up `.env` file from `.env.example`
5. ✅ Create `__init__.py` files

**Commands**:
```bash
cd backend
poetry install
cp .env.example .env
# Edit .env with your database credentials
```

**Deliverable**: Clean project structure ready for code

---

### Step 2: Configuration & Database Setup
**Goal**: Configure application and connect to PostgreSQL

**Tasks**:
1. Create `app/config.py` (settings management)
2. Create `app/database.py` (database connections)
3. Set up PostgreSQL database
4. Test database connection
5. Set up Redis connection
6. Test Redis connection

**Commands**:
```bash
# Create PostgreSQL database
psql -U postgres
CREATE DATABASE ics_threat_detection;
CREATE USER ics_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ics_threat_detection TO ics_user;

# Test connections
poetry run python -c "from app.database import engine; print('DB OK')"
```

**Deliverable**: Working database and Redis connections

---

### Step 3: SQLAlchemy Models
**Goal**: Define database schema

**Tasks**:
1. Create `app/models/__init__.py`
2. Create `app/models/alert.py` (Alert + AlertSource models)
3. Create `app/models/fl_round.py` (FLRound + FLClient models)
4. Create `app/models/prediction.py` (Prediction + PredictedTechnique models)
5. Create `app/models/network_data.py` (NetworkData model)

**Deliverable**: All database models defined

---

### Step 4: Database Migration
**Goal**: Create database tables

**Tasks**:
1. Initialize Alembic
2. Generate initial migration
3. Apply migration
4. Verify tables created

**Commands**:
```bash
poetry run alembic init alembic
poetry run alembic revision --autogenerate -m "Initial schema"
poetry run alembic upgrade head

# Verify
psql -U ics_user -d ics_threat_detection -c "\dt"
```

**Deliverable**: Database tables created and ready

---

### Step 5: Pydantic Schemas
**Goal**: Define request/response schemas

**Tasks**:
1. Create `app/schemas/__init__.py`
2. Create `app/schemas/alert.py` (Alert schemas)
3. Create `app/schemas/fl_status.py` (FL schemas)
4. Create `app/schemas/prediction.py` (Prediction schemas)
5. Create `app/schemas/context.py` (Context schemas)

**Deliverable**: All Pydantic schemas defined

---

### Step 6: Basic FastAPI App
**Goal**: Create minimal working API

**Tasks**:
1. Create `app/main.py` (FastAPI app)
2. Add CORS middleware
3. Create health check endpoint
4. Test with `uvicorn`

**Commands**:
```bash
poetry run uvicorn app.main:app --reload --port 8000
# Visit http://localhost:8000/docs
```

**Deliverable**: FastAPI app running with Swagger docs

---

## Phase 2: Repository Layer (Day 3)

### Step 7: Repository Pattern
**Goal**: Create data access layer

**Tasks**:
1. Create `app/repositories/__init__.py`
2. Create `app/repositories/alert_repository.py`
3. Create `app/repositories/fl_repository.py`
4. Create `app/repositories/prediction_repository.py`
5. Write basic CRUD operations

**Deliverable**: Repository layer with database operations

---

### Step 8: Seed Data
**Goal**: Load mock data into database

**Tasks**:
1. Create `scripts/seed_database.py`
2. Convert webapp mock data to database format
3. Load 20 sample alerts
4. Load FL round history
5. Load sample predictions

**Commands**:
```bash
poetry run python scripts/seed_database.py
```

**Deliverable**: Database populated with test data

---

## Phase 3: API Endpoints (Day 4-5)

### Step 9: Alerts API
**Goal**: Implement alerts endpoints

**Tasks**:
1. Create `app/api/alerts.py`
2. Implement `GET /api/alerts` (with filtering, pagination)
3. Implement `GET /api/alerts/{id}`
4. Implement `PUT /api/alerts/{id}/status`
5. Implement `GET /api/alerts/stats`
6. Add dependencies injection
7. Test all endpoints

**Deliverable**: Working alerts API

---

### Step 10: FL Status API
**Goal**: Implement FL endpoints

**Tasks**:
1. Create `app/api/fl_status.py`
2. Implement `GET /api/fl/rounds/current`
3. Implement `GET /api/fl/rounds/history`
4. Implement `GET /api/fl/clients`
5. Implement `GET /api/fl/privacy-metrics`
6. Implement `POST /api/fl/rounds/trigger`
7. Test all endpoints

**Deliverable**: Working FL API

---

### Step 11: Predictions API
**Goal**: Implement predictions endpoints

**Tasks**:
1. Create `app/api/predictions.py`
2. Implement `GET /api/predictions`
3. Implement `GET /api/predictions/latest`
4. Implement `GET /api/mitre/graph`
5. Implement `GET /api/mitre/technique/{id}`
6. Test all endpoints

**Deliverable**: Working predictions API

---

### Step 12: System API
**Goal**: Implement system endpoints

**Tasks**:
1. Add `GET /api/system/status` to `app/main.py`
2. Calculate real-time metrics
3. Test endpoint

**Deliverable**: System status endpoint working

---

## Phase 4: WebSocket Integration (Day 6-7)

### Step 13: WebSocket Manager
**Goal**: Create WebSocket infrastructure

**Tasks**:
1. Create `app/services/__init__.py`
2. Create `app/services/websocket_manager.py`
3. Implement connection management
4. Implement channel-based broadcasting
5. Test WebSocket connection

**Deliverable**: WebSocket manager ready

---

### Step 14: WebSocket Endpoint
**Goal**: Create WebSocket endpoint

**Tasks**:
1. Create `app/api/websocket.py`
2. Implement `WS /ws` endpoint
3. Handle client connections
4. Test with WebSocket client

**Commands**:
```bash
# Test with wscat
npm install -g wscat
wscat -c ws://localhost:8000/ws
```

**Deliverable**: WebSocket endpoint working

---

### Step 15: Kafka Consumer (Optional for Phase 1)
**Goal**: Bridge Kafka to WebSocket

**Tasks**:
1. Create `app/services/kafka_consumer.py`
2. Implement Kafka consumer
3. Forward messages to WebSocket
4. Test message flow

**Note**: Can be skipped initially and simulated with direct WebSocket broadcasts

**Deliverable**: Kafka → WebSocket bridge (or simulation)

---

## Phase 5: Service Layer (Day 8-9)

### Step 16: Alert Service
**Goal**: Business logic for alerts

**Tasks**:
1. Create `app/services/alert_service.py`
2. Implement alert creation with WebSocket broadcast
3. Implement alert update with WebSocket broadcast
4. Implement alert statistics calculation
5. Test service methods

**Deliverable**: Alert service with WebSocket integration

---

### Step 17: FL Service
**Goal**: Business logic for FL

**Tasks**:
1. Create `app/services/fl_service.py`
2. Implement round triggering
3. Implement progress updates with WebSocket
4. Implement client status updates
5. Test service methods

**Deliverable**: FL service with WebSocket integration

---

### Step 18: Prediction Service
**Goal**: Business logic for predictions

**Tasks**:
1. Create `app/services/prediction_service.py`
2. Implement prediction creation
3. Implement graph queries (mock Neo4j initially)
4. Test service methods

**Deliverable**: Prediction service working

---

## Phase 6: Context Buffer (Day 10)

### Step 19: Context Buffer Service
**Goal**: Redis-based context storage

**Tasks**:
1. Create `app/services/context_buffer.py`
2. Implement 60-second rolling window
3. Implement context storage
4. Implement context retrieval
5. Test Redis operations

**Deliverable**: Context buffer service working

---

### Step 20: Context API
**Goal**: Context endpoints

**Tasks**:
1. Create `app/api/context.py`
2. Implement `GET /api/context/{facility_id}/current`
3. Implement `GET /api/context/{alert_id}/evidence`
4. Implement `GET /api/context/{alert_id}/timeline`
5. Test endpoints

**Deliverable**: Context API working

---

## Phase 7: Demo Scenarios (Day 11-12)

### Step 21: Demo API
**Goal**: Demo scenario triggers

**Tasks**:
1. Create `app/api/demo.py`
2. Implement `POST /api/demo/scenarios/port-scan`
3. Implement `POST /api/demo/scenarios/fl-round`
4. Implement `POST /api/demo/scenarios/multi-stage`
5. Implement `GET /api/demo/status`
6. Test scenarios

**Deliverable**: Demo API working

---

### Step 22: Demo Orchestration
**Goal**: Coordinate demo scenarios

**Tasks**:
1. Create `app/services/demo_service.py`
2. Implement port scan simulation
3. Implement FL round simulation
4. Implement multi-stage attack simulation
5. Test all scenarios

**Deliverable**: All demo scenarios working

---

## Phase 8: WebApp Integration (Day 13-14)

### Step 23: WebApp API Client
**Goal**: Connect webapp to backend

**Tasks**:
1. Create `webapp/lib/api-client.ts`
2. Create `webapp/hooks/use-websocket.ts`
3. Create `webapp/.env.local`
4. Test API client

**Deliverable**: WebApp can call backend API

---

### Step 24: Dashboard Integration
**Goal**: Replace mock data in dashboard

**Tasks**:
1. Update `webapp/app/page.tsx`
2. Replace mock data with API calls
3. Add WebSocket integration
4. Test real-time updates

**Deliverable**: Dashboard showing real data

---

### Step 25: Alerts Page Integration
**Goal**: Replace mock data in alerts page

**Tasks**:
1. Update `webapp/app/alerts/page.tsx`
2. Replace mock data with API calls
3. Add WebSocket for real-time alerts
4. Test filtering, pagination, search

**Deliverable**: Alerts page fully functional

---

### Step 26: FL Status Integration
**Goal**: Replace mock data in FL page

**Tasks**:
1. Update `webapp/app/fl-status/page.tsx`
2. Replace mock data with API calls
3. Add WebSocket for live progress
4. Test FL round triggering

**Deliverable**: FL status page fully functional

---

### Step 27: Attack Graph Integration
**Goal**: Replace mock data in attack graph

**Tasks**:
1. Update `webapp/app/attack-graph/page.tsx`
2. Replace mock data with API calls
3. Add WebSocket for predictions
4. Test graph updates

**Deliverable**: Attack graph fully functional

---

## Phase 9: Testing & Polish (Day 15-16)

### Step 28: API Testing
**Goal**: Comprehensive API tests

**Tasks**:
1. Create `tests/test_api/test_alerts.py`
2. Create `tests/test_api/test_fl_status.py`
3. Create `tests/test_api/test_predictions.py`
4. Run all tests
5. Fix any issues

**Commands**:
```bash
poetry run pytest tests/
poetry run pytest --cov=app tests/
```

**Deliverable**: All API tests passing

---

### Step 29: Integration Testing
**Goal**: End-to-end testing

**Tasks**:
1. Test complete alert flow
2. Test complete FL round flow
3. Test complete prediction flow
4. Test WebSocket reliability
5. Test demo scenarios (10x runs)

**Deliverable**: All integration tests passing

---

### Step 30: Documentation & Cleanup
**Goal**: Final polish

**Tasks**:
1. Update README.md
2. Add API documentation
3. Add code comments
4. Clean up unused code
5. Verify all environment variables

**Deliverable**: Production-ready backend

---

## Quick Start Commands Summary

### Initial Setup
```bash
# 1. Install dependencies
cd backend
poetry install

# 2. Set up environment
cp .env.example .env
# Edit .env with your credentials

# 3. Create database
psql -U postgres
CREATE DATABASE ics_threat_detection;
CREATE USER ics_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ics_threat_detection TO ics_user;
\q

# 4. Run migrations
poetry run alembic init alembic
poetry run alembic revision --autogenerate -m "Initial schema"
poetry run alembic upgrade head

# 5. Seed database
poetry run python scripts/seed_database.py

# 6. Start server
poetry run uvicorn app.main:app --reload --port 8000
```

### Development Workflow
```bash
# Start backend
cd backend
poetry run uvicorn app.main:app --reload --port 8000

# Start frontend (in another terminal)
cd webapp
pnpm dev

# Run tests
poetry run pytest
```

---

## Progress Tracking

### Phase 1: Foundation ⬜
- [ ] Step 1: Project initialization
- [ ] Step 2: Configuration & database
- [ ] Step 3: SQLAlchemy models
- [ ] Step 4: Database migration
- [ ] Step 5: Pydantic schemas
- [ ] Step 6: Basic FastAPI app

### Phase 2: Repository ⬜
- [ ] Step 7: Repository pattern
- [ ] Step 8: Seed data

### Phase 3: API Endpoints ⬜
- [ ] Step 9: Alerts API
- [ ] Step 10: FL Status API
- [ ] Step 11: Predictions API
- [ ] Step 12: System API

### Phase 4: WebSocket ⬜
- [ ] Step 13: WebSocket manager
- [ ] Step 14: WebSocket endpoint
- [ ] Step 15: Kafka consumer (optional)

### Phase 5: Service Layer ⬜
- [ ] Step 16: Alert service
- [ ] Step 17: FL service
- [ ] Step 18: Prediction service

### Phase 6: Context Buffer ⬜
- [ ] Step 19: Context buffer service
- [ ] Step 20: Context API

### Phase 7: Demo ⬜
- [ ] Step 21: Demo API
- [ ] Step 22: Demo orchestration

### Phase 8: WebApp Integration ⬜
- [ ] Step 23: WebApp API client
- [ ] Step 24: Dashboard integration
- [ ] Step 25: Alerts page integration
- [ ] Step 26: FL status integration
- [ ] Step 27: Attack graph integration

### Phase 9: Testing ⬜
- [ ] Step 28: API testing
- [ ] Step 29: Integration testing
- [ ] Step 30: Documentation

---

## Estimated Timeline

- **Phase 1-2**: 2-3 days (Foundation + Repository)
- **Phase 3**: 2 days (API Endpoints)
- **Phase 4**: 2 days (WebSocket)
- **Phase 5**: 2 days (Service Layer)
- **Phase 6**: 1 day (Context Buffer)
- **Phase 7**: 2 days (Demo)
- **Phase 8**: 2 days (WebApp Integration)
- **Phase 9**: 2 days (Testing & Polish)

**Total**: ~15-16 days for complete implementation

---

## Success Criteria

### Minimum Success (MVP)
- ✅ All API endpoints working
- ✅ WebSocket real-time updates
- ✅ WebApp displays real data
- ✅ Basic demo scenarios work

### Target Success
- ✅ All features implemented
- ✅ Context buffer working
- ✅ FL integration complete
- ✅ All tests passing
- ✅ Demo scenarios reliable

### Stretch Success
- ✅ Performance optimized
- ✅ Comprehensive documentation
- ✅ Production-ready deployment
- ✅ Monitoring and logging

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** Implementation Roadmap
