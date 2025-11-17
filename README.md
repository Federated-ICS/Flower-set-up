# 🛡️ FedICS — Federated Intrusion Detection for Critical Systems

> **Privacy-preserving collaborative threat detection for industrial control systems using federated learning.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-required-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-IAS%20Phase%202-brightgreen.svg)]()

🎯 **IEEE IAS Technical Challenge Phase 2 Prototype**

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

👋 **New contributor?** Start with the step-by-step runbook in [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) for an end-to-end setup (clone → configure → run → verify).

```bash
# 1. Clone and enter repo
git clone https://github.com/Federated-ICS/Flower-set-up.git
cd Flower-set-up

# 2. Copy environment template
cp .env.example .env

# 3. Start the full stack
docker compose up --build

# 4. Access services:
# - Dashboard: http://localhost:3000 (Next.js UI)
# - API Docs: http://localhost:8000/docs (FastAPI Backend)
# - Flower Server: http://localhost:8080 (FL Orchestrator)
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

**For deeper architecture details**: See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md)

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
| [`docs/GETTING_STARTED.md`](docs/GETTING_STARTED.md) | New-developer runbook (clone → configure → run → verify) |
| [`docs/PROJECT_OVERVIEW.md`](docs/PROJECT_OVERVIEW.md) | High-level system intro, quick start, features |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Kafka topics, service responsibilities, data flows |
| [`DEMO.md`](DEMO.md) | 5-minute hackathon demo script |
| [`IAS_TECHNICAL_SUMMARY.md`](IAS_TECHNICAL_SUMMARY.md) | IEEE IAS competition technical summary |

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

## 🎯 IEEE IAS Competition Scope

**This is a Phase 2 prototype demonstrating core innovation** — privacy-preserving federated learning for industrial cybersecurity.

### ✅ What Works
- Core FL + streaming pipeline fully functional
- All microservices containerized and orchestrated
- Next.js dashboard with real-time WebSocket updates
- FastAPI backend with PostgreSQL, Redis, Neo4j
- Multi-layer detection (LSTM, Isolation Forest, Physics Rules)
- Differential privacy tracking (ε=0.5 per round)

### 🚧 Production Features (Intentionally Skipped for Demo)
- Authentication/Authorization (not needed for competition demo)
- TLS/SSL encryption (HTTP sufficient for local demo)
- Enterprise monitoring (Prometheus/Grafana)
- Real ICS datasets (synthetic data demonstrates concept)
- Actual Graph Neural Networks (weighted scoring placeholder)
- Byzantine fault tolerance (Phase 3 roadmap)

**Focus**: Core innovation (federated learning for ICS) over production scaffolding.

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
   - FastAPI REST: `http://localhost:8000` (endpoints: `/anomalies`, `/classifications`, `/predictions`, `/alerts`, `/fl-events`)
   - FastAPI WebSocket: `ws://localhost:8000/ws/events`
   - Next.js dashboard: `http://localhost:3000`
   - PostgreSQL: `postgres://postgres:postgres@localhost:5432/ics_threat_detection`
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
python services/severity_predictor/main.py

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
│   ├── severity_predictor/       # Severity forecaster (weighted scoring)
│   └── fastapi_backend/          # REST + WebSocket API
│
├── dashboard/                    # Next.js frontend with React 19
│   ├── app/                      # Next.js App Router pages
│   ├── components/               # React components (Radix UI)
│   ├── utils/                    # Utilities and mock data
│   └── tdd/                      # Test-driven development docs
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
**Last Updated**: November 17, 2025

---

## 🏆 IEEE IAS Technical Challenge

This project is submitted for **IEEE Industry Applications Society (IAS) Technical Challenge Phase 2** in the **System Control & Cybersecurity** category.

**Core Innovation**: Privacy-preserving collaborative learning for critical infrastructure defense.

See [`IAS_TECHNICAL_SUMMARY.md`](IAS_TECHNICAL_SUMMARY.md) for complete technical documentation and [`DEMO.md`](DEMO.md) for presentation script.

**Questions?** Open an issue or check [`docs/`](docs/) for detailed guides.
