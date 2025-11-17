# FedICS Cleanup & Reorganization Plan

## Executive Summary

Your project is **80% functional** but suffers from:
- Duplicate implementations (2 dashboards, 2 backends)
- Missing operational pieces (configs, tests, CI/CD)
- Misleading naming (GNN predictor doesn't use GNNs)
- Security gaps (hardcoded secrets, no auth)

**Recommendation**: Phase 1 cleanup (consolidate duplicates, add configs) → Phase 2 hardening (security, tests, CI) → Phase 3 enhancements (real GNN, real datasets).

---

## Current State Assessment

### ✅ What Works Well
1. **Core FL Pipeline**
   - Flower server/clients implemented correctly
   - FedAvg aggregation functional
   - Differential privacy (gradient clipping + Gaussian noise)
   - Epsilon tracking via Kafka
   
2. **Streaming Architecture**
   - Kafka topics properly defined
   - Microservices communicate via events
   - Data flow: simulator → detectors → classifier → predictor → backend
   
3. **Detection Stack**
   - 3 complementary anomaly detectors (LSTM, IForest, Physics)
   - Threat classifier aggregates votes
   - Alert generation works

### ⚠️ Issues Identified

| Issue | Severity | Impact |
|-------|----------|--------|
| Duplicate dashboards (Vite + Next.js) | HIGH | Confusing which to develop |
| Duplicate backends (`services/` + `dashboard/backend/`) | HIGH | Split development effort |
| No `.env.example` | MEDIUM | Hard to configure |
| Hardcoded secrets in `docker-compose.yml` | HIGH | Security risk |
| GNN predictor doesn't use GNNs | MEDIUM | Misleading name |
| No authentication | HIGH | Not production-ready |
| Missing integration tests | MEDIUM | Hard to catch regressions |
| No CI/CD | LOW | Manual testing only |
| Dashboard confusion | MEDIUM | Multiple incomplete UIs |

---

## File Organization Analysis

### Current Structure
```
Flower-set-up/
├── src/                    ✅ Well-organized core FL code
├── services/               ✅ Microservices properly separated
├── dashboard/
│   ├── src/               ⚠️ Vite React (prototype)
│   ├── frontend/          ⚠️ Next.js (production-ready)
│   └── backend/           ⚠️ Duplicate FastAPI backend
├── docker/                 ✅ Shared Dockerfile
├── docs/                   ✅ Some architecture docs
├── .venv/                  ⚠️ Should not be committed (in .gitignore)
├── .env.example            ❌ MISSING
├── tests/                  ❌ MISSING (only test_setup.py at root)
├── scripts/                ❌ MISSING (utility scripts scattered)
└── examples/               ❌ MISSING (sample usage)
```

### Recommended Structure
```
Flower-set-up/
├── src/                    # Core federated learning code
│   ├── server/
│   ├── client/
│   ├── models/
│   ├── data/
│   └── streaming/
│
├── services/               # Kafka microservices
│   ├── network_simulator/
│   ├── anomaly_lstm/
│   ├── anomaly_iforest/
│   ├── anomaly_physics/
│   ├── threat_classifier/
│   ├── severity_predictor/ # 🔄 RENAME from gnn_predictor
│   └── backend/            # 🔄 CONSOLIDATE FastAPI backends
│
├── dashboard/              # 🔄 CHOOSE ONE FRONTEND
│   ├── src/               # Option A: Keep Vite (simpler)
│   └── ...                # Option B: Keep Next.js (more features)
│
├── docker/                 # Container definitions
│   ├── python-service.Dockerfile
│   ├── dashboard.Dockerfile
│   └── backend.Dockerfile
│
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md     ✅ Exists
│   ├── PROJECT_OVERVIEW.md ✅ New
│   ├── CLEANUP_PLAN.md     ✅ This file
│   ├── API.md              ❌ Document REST endpoints
│   ├── DEPLOYMENT.md       ❌ Production deployment guide
│   └── DEVELOPMENT.md      ❌ Local dev setup
│
├── tests/                  # 🆕 Consolidated tests
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── scripts/                # 🆕 Utility scripts
│   ├── setup_dev.sh
│   ├── clear_kafka.sh
│   ├── seed_db.py
│   └── run_integration_tests.sh
│
├── examples/               # 🆕 Sample usage
│   ├── custom_detector.py
│   ├── kafka_consumer.py
│   └── fl_client_custom.py
│
├── .github/                # 🆕 CI/CD
│   └── workflows/
│       ├── ci.yml
│       └── docker-publish.yml
│
├── .env.example            # 🆕 Configuration template
├── .gitignore              ✅ Exists
├── docker-compose.yml      ✅ Exists
├── docker-compose.dev.yml  # 🆕 Local development overrides
├── Makefile                # 🆕 Common commands
├── pyproject.toml          # 🆕 Python packaging
├── README.md               ✅ Exists
└── requirements.txt        ✅ Exists
```

---

## Phased Cleanup Plan

### Phase 1: Immediate Cleanup (High Priority)

#### 1.1 Consolidate Dashboards
**Decision Required**: Choose ONE frontend approach

**Option A: Keep Vite React (simpler)**
```bash
# Keep: dashboard/src/, dashboard/index.html, dashboard/vite.config.js
# Delete: dashboard/frontend/ (entire Next.js app)
```

**Option B: Keep Next.js (more features)**
```bash
# Keep: dashboard/frontend/
# Delete: dashboard/src/, dashboard/index.html, dashboard/vite.config.js, dashboard/package.json
# Move: dashboard/frontend/* → dashboard/
```

**Recommendation**: **Option B (Next.js)** because:
- More component reusability
- Better routing
- TypeScript types already defined
- More production-ready

#### 1.2 Consolidate Backends
**Current State**: Two FastAPI backends
- `services/fastapi_backend/` (8 files, basic)
- `dashboard/backend/` (50+ files, full-featured with Redis/Neo4j)

**Decision**: **Keep `dashboard/backend/`**, delete `services/fastapi_backend/`

**Action**:
```bash
# 1. Move dashboard/backend/ → services/backend/
mv dashboard/backend services/backend

# 2. Update docker-compose.yml to point to services/backend
# 3. Update Dockerfile paths

# 3. Delete old backend
rm -rf services/fastapi_backend
```

#### 1.3 Create Configuration Files
```bash
# Create .env.example (done above)
# Create docker-compose.dev.yml for local overrides
# Create Makefile for common commands
```

#### 1.4 Rename Misleading Services
```bash
# Rename services/gnn_predictor/ → services/severity_predictor/
mv services/gnn_predictor services/severity_predictor

# Update docker-compose.yml references
# Update Python imports if any
```

#### 1.5 Remove Sensitive Data from Docker Compose
**Current Issue**: Secrets in plain text
```yaml
# BAD:
environment:
  - POSTGRES_PASSWORD=postgres
```

**Fix**: Use `.env` file
```yaml
# GOOD:
environment:
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

---

### Phase 2: Structural Improvements (Medium Priority)

#### 2.2 Add Scripts Directory
```bash
mkdir scripts
```

**Useful Scripts**:
- `scripts/setup_dev.sh` - One-command local dev setup
- `scripts/clear_kafka.sh` - Reset Kafka topics
- `scripts/seed_db.py` - Populate database with test data
- `scripts/run_integration_tests.sh` - Full pipeline validation

---

### Phase 4: Enhancements (Nice-to-Have)

#### 4.1 Implement Real GNN
Replace `services/severity_predictor/` with actual Graph Neural Network:
- PyTorch Geometric or DGL
- ATT&CK graph embeddings
- Node classification for technique prediction

#### 4.2 Add Real Datasets
- CICIDS2017 / CICIDS2018
- NSL-KDD
- UNSW-NB15
- Custom ICS/SCADA datasets (Modbus, DNP3)

#### 4.3 Add Time-Series Storage
- Integrate IoTDB for sensor data
- TimescaleDB as PostgreSQL extension
- InfluxDB for metrics

#### 4.4 Add Graph Database
- Complete Neo4j integration
- Store ATT&CK techniques as graph
- Query attack paths

---

## Files to Delete

### Immediate Deletions
```bash
# Choose based on dashboard decision:
rm -rf dashboard/src/          # If keeping Next.js
rm -rf dashboard/frontend/     # If keeping Vite

# Backend consolidation
rm -rf services/fastapi_backend/  # After moving to dashboard/backend

# Duplicate documentation (check for stale content)
# dashboard/backend/docs/* may duplicate docs/
```

### Files to Keep But Relocate
```bash
# Move utility scripts to scripts/
mv dashboard/backend/scripts/* scripts/

# Move tests to consolidated tests/
mv dashboard/backend/tests/* tests/

# Move additional docs if not duplicates
```

---

## Critical Gaps to Address

### 1. Missing Documentation
- [ ] API documentation (OpenAPI/Swagger is auto-generated, but need narrative docs)
- [ ] Deployment guide (production deployment steps)
- [ ] Development guide (local setup, common tasks)
- [ ] Troubleshooting guide (common errors)

### 2. Missing Tests
- [ ] Unit tests for all models
- [ ] Integration tests for Kafka pipeline
- [ ] End-to-end tests for FL rounds
- [ ] API contract tests
- [ ] Dashboard component tests

### 3. Missing Configuration
- [ ] `.env.example` (created above)
- [ ] `docker-compose.dev.yml` (local dev overrides)
- [ ] `docker-compose.prod.yml` (production config)
- [ ] Service-specific configs (detector thresholds, FL hyperparameters)

### 4. Security Gaps
- [ ] No authentication/authorization
- [ ] Secrets in plaintext
- [ ] No TLS/SSL for Kafka
- [ ] No rate limiting
- [ ] No input validation in some services
- [ ] No audit logging

### 5. Operational Gaps
- [ ] No health checks in containers
- [ ] No graceful shutdown handling
- [ ] No backup/restore procedures
- [ ] No monitoring/alerting
- [ ] No log aggregation

---

## Recommended Actions (Prioritized)

### Week 1: Core Cleanup
1. ✅ Create `.env.example`
2. ✅ Choose and consolidate dashboards (Next.js chosen, Vite removed)
3. ⬜ Consolidate backends (keep `dashboard/backend`)
4. ⬜ Rename `gnn_predictor` → `severity_predictor`
5. ⬜ Move secrets to `.env` file
6. ⬜ Update `docker-compose.yml` to use env vars

### Week 2: Structure & Tests
7. ⬜ Create `tests/` directory with unit/integration split
8. ⬜ Add integration test for full pipeline
9. ⬜ Create `scripts/` directory with dev utilities
10. ⬜ Add `Makefile` for common commands
11. ⬜ Create `examples/` directory with sample usage

### Week 3: Documentation
12. ⬜ Write `docs/API.md` (REST endpoint reference)
13. ⬜ Write `docs/DEPLOYMENT.md` (production guide)
14. ⬜ Write `docs/DEVELOPMENT.md` (local dev setup)
15. ⬜ Update main `README.md` with cleanup results
16. ⬜ Add code comments to complex functions

### Week 4: Security & CI
17. ⬜ Add JWT authentication to FastAPI
18. ⬜ Configure Kafka SASL/SSL
19. ⬜ Create GitHub Actions CI pipeline
20. ⬜ Add health check endpoints
21. ⬜ Implement graceful shutdown

---

## Proposed Project Names

Current: **"Flower-set-up"** (generic, not memorable)

### Name Suggestions:

1. **FedICS** ✅ (Federated ICS Security)
   - Clear, professional, domain-specific
   
2. **SentinelFL** (Sentinel + Federated Learning)
   - Implies watchful protection

3. **DistillIDS** (Distributed Intrusion Detection System)
   - Plays on "distillation" (FL term) + IDS

4. **HiveMind** (Collective intelligence)
   - Evokes distributed learning

5. **GuardianNet** (Guardian + Network)
   - Implies protection

**Recommendation**: **FedICS** — Clear, professional, searchable, domain-relevant.

---

## Success Metrics

After cleanup, you should be able to:
- [ ] Run entire stack with `docker compose up`
- [ ] Configure via `.env` file (no code changes)
- [ ] Run tests with `make test`
- [ ] Understand data flow from reading docs
- [ ] Add new detector in <1 hour
- [ ] Deploy to production with confidence

---

## Questions to Resolve

1. **Dashboard Choice**: Vite (simple) or Next.js (feature-rich)?
   - **Recommendation**: Next.js (better architecture)

2. **Backend Choice**: `services/fastapi_backend` or `dashboard/backend`?
   - **Recommendation**: `dashboard/backend` (more complete)

3. **GNN Implementation**: Keep mock or build real GNN?
   - **Recommendation**: Phase 4 enhancement (real GNN)

4. **Dataset Strategy**: Synthetic only or integrate real datasets?
   - **Recommendation**: Start synthetic, add real data adapters later

5. **Deployment Target**: Docker Compose, Kubernetes, or both?
   - **Recommendation**: Compose for dev/demo, K8s for production

---

## Next Steps

1. **Review this plan** and make decisions on:
   - Dashboard choice (Vite vs Next.js)
   - Backend consolidation approach
   - Priority order for tasks

2. **Execute Week 1 tasks** (core cleanup)

3. **Test after each change** to ensure nothing breaks

4. **Update documentation** as you go

5. **Consider opening GitHub issues** for each task to track progress

---

**Estimated Effort**: 4 weeks (1 person, part-time) to complete Phases 1-3.

**Result**: Production-ready, maintainable, understandable codebase with clear architecture.
