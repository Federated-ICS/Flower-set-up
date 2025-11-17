# 🛡️ FedICS — Federated Intrusion Detection for Critical Systems

> **A streaming-first, privacy-preserving network attack detection platform combining federated learning, Kafka event processing, and real-time threat intelligence.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-research%20prototype-yellow.svg)]()

---

## 🎯 What This System Does

**FedICS** (Federated ICS Security) demonstrates how industrial control systems (ICS) and critical infrastructure can **detect, classify, and predict network attacks** while keeping sensitive operational data private through **federated learning**.

**The platform**:
- 🔍 Detects anomalies using **3 detection engines** (LSTM Autoencoder, Isolation Forest, Physics Rules)
- 🏷️ Classifies threats automatically (benign, probe, DoS)
- 🧠 Predicts attack severity and next-hop using graph-based reasoning
- 🌐 Streams events through **Apache Kafka** for real-time processing
- 🔒 Trains ML models **without centralizing data** via Flower federated learning
- 🎯 Provides differential privacy guarantees (ε-δ accounting)
- 📊 Visualizes everything in a live dashboard (WebSocket + REST API)

**Use Cases**: Security Operations Centers (SOCs), distributed ICS/SCADA networks, privacy-sensitive multi-party ML, threat intelligence sharing.

---

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Clone and enter repo
git clone https://github.com/Federated-ICS/Flower-set-up.git
cd Flower-set-up

# 2. Copy environment template
cp .env.example .env

# 3. Start the full stack
docker compose up --build

# 4. Access services:
# - Dashboard: http://localhost:3000
# - API Docs: http://localhost:8000/docs
# - Flower Server: http://localhost:8080
```

**What happens:**
1. Network simulator generates synthetic ICS traffic → Kafka
2. 3 anomaly detectors score flows independently → Kafka
3. Threat classifier aggregates votes → attack labels
4. Severity predictor forecasts impact → alerts
5. FastAPI backend persists events → PostgreSQL
6. Dashboard renders live alerts + FL health metrics

---

## 📊 System Architecture (30-Second Version)

```
┌─────────────────┐
│ Network Sim     │──► network_data (Kafka topic)
└─────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│ LSTM │ IForest │ Physics Rules          │──► anomalies
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Threat Classify │──► attack_classified
└─────────────────┘
         │
         ▼
┌─────────────────┐
│ Severity Predict│──► attack_predicted + alerts
└─────────────────┘
         │
         ▼
┌─────────────────────────┐
│ FastAPI Backend         │──► PostgreSQL + WebSocket
└─────────────────────────┘
         │
         ▼
┌─────────────────┐
│ React Dashboard │  (Live threat feed)
└─────────────────┘

Parallel FL Loop:
┌──────────────┐      ┌─────────────┐
│ Flower Server│◄────►│ 3 DP Clients│──► fl_events (Kafka)
└──────────────┘      └─────────────┘
```

**For deeper architecture details**: See [`docs/ARCHITECTURE_DEEP_DIVE.md`](docs/ARCHITECTURE_DEEP_DIVE.md)

---

## 📁 What Lives in This Repo

| Directory | Purpose |
|-----------|---------|
| `src/` | Core federated learning code (Flower server/clients, models, data utils, Kafka streaming) |
| `services/` | Kafka microservices (simulator, detectors, classifier, predictor, backend API) |
| `dashboard/` | React/Next.js UI + FastAPI backend for visualization |
| `docker/` | Shared Dockerfiles for Python services |
| `docs/` | Architecture deep dives, cleanup plans, deployment guides |
| Root scripts | `run_server.py`, `run_client.py`, `simulate_federated_learning.py` |

## Repository layout (high level)
```
├── docker-compose.yml                 # Launches the full stack
├── docker/python-service.Dockerfile   # Base image for Python microservices
├── docs/ARCHITECTURE.md               # Kafka topics & service responsibilities
├── services/                          # Streaming microservices + FastAPI backend
├── src/                               # Flower server/clients, streaming utilities
├── dashboard/                         # React frontend
├── run_server.py / run_client.py      # Local Flower entrypoints
└── simulate_federated_learning.py     # CLI to run FL simulation
```

---

## 🔑 Key Features

### ✅ Multi-Model Anomaly Detection
- **LSTM Autoencoder**: Temporal behavior analysis (60-timestep windows)
- **Isolation Forest**: Point anomaly detection (tree-based, unsupervised)
- **Physics Rules**: Deterministic safety checks (surge detection, impossible ports)

### ✅ Federated Learning with Differential Privacy
- **Flower framework** with FedAvg strategy
- **3 distributed clients** (simulate different facilities/sites)
- **Gradient clipping + Gaussian noise** for (ε,δ)-DP guarantees
- **Epsilon tracking** published to Kafka for audit trails

### ✅ Real-Time Streaming Pipeline
- **Apache Kafka** backbone with 6 topics:
  - `network_data`: Raw flow telemetry
  - `anomalies`: Detector outputs (scores + context)
  - `attack_classified`: Threat labels (benign/probe/DoS)
  - `attack_predicted`: Severity forecasts
  - `alerts`: High-priority notifications
  - `fl_events`: FL round metrics (accuracy, loss, DP budgets)
- **Event schemas** centralized in `src/streaming/event_models.py`

### ✅ Production-Ready API & Dashboard
- **FastAPI backend**: REST + WebSocket (live event push)
- **PostgreSQL persistence**: Alerts, classifications, predictions, FL metrics
- **React/Next.js dashboard**: Real-time threat feed, FL health, attack timelines

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) | High-level system intro, quick start, features |
| [`docs/ARCHITECTURE_DEEP_DIVE.md`](docs/ARCHITECTURE_DEEP_DIVE.md) | Component inventory, data flows, event schemas |
| [`docs/CLEANUP_PLAN.md`](docs/CLEANUP_PLAN.md) | Identified issues, recommended refactors, roadmap |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Kafka topics, service responsibilities |

---

## ⚙️ Configuration

All services read from environment variables. **Copy `.env.example` → `.env`** and customize:

| Variable | Default | Purpose |
|----------|---------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Kafka broker address |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `FLOWER_SERVER_ADDRESS` | `flower-server:8080` | Federated learning server endpoint |
| `FL_NUM_ROUNDS` | `5` | Number of FL training rounds |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Dashboard → Backend URL |

See [`.env.example`](.env.example) for the full list with documentation.

---

## 🚧 Known Issues & Limitations

### Current State
- ✅ Core FL + streaming pipeline functional
- ✅ All microservices containerized
- ⚠️ **Duplicate dashboard implementations** (Vite root + Next.js in `dashboard/frontend/`)
- ⚠️ **Duplicate FastAPI backends** (`services/fastapi_backend/` + `dashboard/backend/`)
- ⚠️ Severity predictor doesn't use actual GNNs (just weighted scoring)
- ⚠️ No authentication/authorization
- ⚠️ Secrets hardcoded in `docker-compose.yml`
- ❌ Neo4j & IoTDB integrations incomplete
- ❌ No CI/CD pipelines

### Recommended Cleanup Actions
1. **Consolidate dashboards** → Choose Vite OR Next.js (recommend Next.js)
2. **Consolidate backends** → Merge into single FastAPI app
3. **Add authentication** → JWT tokens, API keys
4. **Externalize secrets** → Use `.env`, Docker secrets, or Vault
5. **Add integration tests** → End-to-end pipeline validation

See [`docs/CLEANUP_PLAN.md`](docs/CLEANUP_PLAN.md) for detailed 4-week roadmap.

---

## Prerequisites
- Docker and Docker Compose
- ~8 GB free RAM for Kafka, PostgreSQL, and TensorFlow-based services
- For local (non-Docker) development: Python 3.11, Node.js 18+, and access to Kafka/PostgreSQL (or override with env vars)

## Run the full stack with Docker Compose
1. Build and start everything:
   ```bash
   docker compose up --build
   ```
2. Services to expect:
   - Flower server: `http://localhost:8080`
   - FastAPI REST: `http://localhost:8000` (collections: `/anomalies`, `/classifications`, `/predictions`, `/alerts`, `/fl-events`)
   - FastAPI WebSocket: `ws://localhost:8000/ws/events`
   - React dashboard: `http://localhost:4173`
   - PostgreSQL: `postgres://postgres:postgres@localhost:5432/attacks`
3. Stop everything:
   ```bash
   docker compose down
   ```

## 💻 Development Workflow

### Run Locally (Without Docker)

```bash
# 1. Create virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Start infrastructure only (Kafka + Postgres)
docker compose up kafka postgres -d

# 3. Override Kafka address for local services
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092  # Windows: $env:KAFKA_BOOTSTRAP_SERVERS="localhost:9092"

# 4. Run services individually
python services/network_simulator/main.py
python services/anomaly_lstm/main.py
python services/anomaly_iforest/main.py
python services/anomaly_physics/main.py
python services/threat_classifier/main.py
python services/gnn_predictor/main.py

# 5. Run Flower server + clients
python run_server.py
python run_client.py --client-id 0 --model-type lstm_autoencoder
python run_client.py --client-id 1 --model-type lstm_autoencoder
python run_client.py --client-id 2 --model-type isolation_forest
```

### Run FL Simulation (No Kafka Required)

```bash
# Simulate full FL workflow locally
python simulate_federated_learning.py --model-type lstm_autoencoder --num-rounds 3
```

### Run Tests

```bash
# Unit tests
pytest test_setup.py

# Backend API tests (if using dashboard/backend)
cd dashboard/backend
pytest
```

---

## 🏗️ Repository Structure

```
Flower-set-up/
├── src/                          # Core federated learning code
│   ├── server/                   # Flower server (FedAvg aggregation)
│   ├── client/                   # Flower clients (DP-enabled)
│   ├── models/                   # LSTM Autoencoder, Isolation Forest
│   ├── data/                     # Synthetic data generation
│   └── streaming/                # Kafka utilities, event schemas
│
├── services/                     # Kafka microservices
│   ├── network_simulator/        # Traffic generator
│   ├── anomaly_lstm/             # LSTM detector service
│   ├── anomaly_iforest/          # Isolation Forest service
│   ├── anomaly_physics/          # Rule-based detector
│   ├── threat_classifier/        # Attack labeler
│   ├── gnn_predictor/            # Severity forecaster
│   └── fastapi_backend/          # REST + WebSocket API
│
├── dashboard/                    # Frontend + backend UI
│   ├── src/                      # Vite + React (simple version)
│   ├── frontend/                 # Next.js (production version)
│   └── backend/                  # Alternative FastAPI backend
│
├── docker/                       # Shared Dockerfile for Python services
├── docs/                         # Architecture, cleanup plans, guides
│
├── run_server.py                 # Local Flower server entrypoint
├── run_client.py                 # Local Flower client entrypoint
├── simulate_federated_learning.py # FL simulation (no Kafka needed)
├── test_setup.py                 # Basic component tests
│
├── docker-compose.yml            # Full stack orchestration
├── .env.example                  # Configuration template
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## 🤝 Contributing

This is a research prototype. Contributions welcome for:
- Real ICS/SCADA dataset integration (CICIDS, NSL-KDD, Modbus captures)
- Improved threat classification models
- Actual GNN-based prediction (replace mock predictor)
- Security hardening (TLS, authentication, authorization)
- Performance optimization
- Integration tests

---

## 📄 License

[Specify your license here - MIT, Apache 2.0, etc.]

---

## 🙏 Acknowledgments

Built with:
- [Flower](https://flower.dev/) - Federated Learning Framework
- [Apache Kafka](https://kafka.apache.org/) - Event Streaming Platform
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API Framework
- [TensorFlow](https://www.tensorflow.org/) - Deep Learning
- [scikit-learn](https://scikit-learn.org/) - Machine Learning Library
- [React](https://react.dev/) / [Next.js](https://nextjs.org/) - Frontend Frameworks

---

## 📖 Citation

If you use this in research, please cite:

```bibtex
@misc{fedics2025,
  title={FedICS: Federated Intrusion Detection for Critical Systems},
  author={[Your Name]},
  year={2025},
  howpublished={\url{https://github.com/Federated-ICS/Flower-set-up}}
}
```

---

**Project Status**: 🚧 Active Development | **Maturity**: Research Prototype  
**Last Updated**: November 2025

**Questions?** Open an issue or check [`docs/`](docs/) for detailed guides.
