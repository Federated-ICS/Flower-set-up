# 🛡️ FedICS — Federated Intrusion Detection for Critical Systems

**A streaming-first, privacy-preserving network attack detection platform combining federated learning, Kafka event processing, and real-time threat intelligence.**

---

## What This System Does

FedICS (Federated ICS Security) is a research prototype that demonstrates how industrial control systems (ICS) and critical infrastructure can detect, classify, and predict network attacks while keeping sensitive operational data private through **federated learning**.

The platform:
- 🔍 Detects anomalies using **3 detection engines** (LSTM Autoencoder, Isolation Forest, Physics Rules)
- 🏷️ Classifies threats automatically (benign, probe, DoS)
- 🧠 Predicts attack severity and next-hop using graph-based reasoning
- 🌐 Streams events through **Apache Kafka** for real-time processing
- 🔒 Trains ML models **without centralizing data** via Flower federated learning
- 🎯 Provides differential privacy guarantees (ε-δ accounting)
- 📊 Visualizes everything in a live dashboard (WebSocket + REST API)

**Use Cases**: Security Operations Centers (SOCs), distributed ICS/SCADA networks, privacy-sensitive multi-party ML, threat intelligence sharing.

---

## System Architecture (30-Second Version)

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
│ Severity Predictor │──► attack_predicted + alerts
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

---

## Quick Start (5 Minutes)

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM (for Kafka + TensorFlow services)

### Launch Everything
```bash
# 1. Clone and enter repo
git clone https://github.com/Federated-ICS/Flower-set-up.git
cd Flower-set-up

# 2. Copy environment template
cp .env.example .env

# 3. Start the full stack (Kafka, Postgres, FL, detectors, dashboard)
docker compose up --build

# 4. Access services:
# - Dashboard: http://localhost:4173
# - API Docs: http://localhost:8000/docs
# - Flower Server: http://localhost:8080
```

**What happens:**
1. Network simulator generates synthetic ICS traffic → Kafka
2. 3 anomaly detectors score flows independently → Kafka
3. Threat classifier aggregates votes → attack labels
4. Severity predictor forecasts impact → alerts
5. FastAPI backend persists events → PostgreSQL
6. Next.js dashboard renders live alerts + FL health metrics

---

## Repository Structure

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
├── dashboard/                    # Frontend + backend UI
│   ├── src/                      # Vite + React (simple version)
│   ├── frontend/                 # Next.js (production version)
│   └── backend/                  # Alternative FastAPI backend
│
├── docker/                       # Shared Dockerfile for Python services
├── docs/                         # Architecture notes
├── run_server.py                 # Local Flower server entrypoint
├── run_client.py                 # Local Flower client entrypoint
├── simulate_federated_learning.py # FL simulation (no Kafka)
├── docker-compose.yml            # Full stack orchestration
└── requirements.txt              # Python dependencies
```

---

## Key Features

### ✅ Multi-Model Anomaly Detection
- **LSTM Autoencoder**: Temporal behavior analysis (60-timestep windows)
- **Isolation Forest**: Point anomaly detection (tree-based)
- **Physics Rules**: Deterministic safety checks (surge detection, port violations)

### ✅ Federated Learning with Differential Privacy
- **Flower framework** with FedAvg strategy
- **3 distributed clients** (simulate different facilities)
- **Gradient clipping + Gaussian noise** for (ε,δ)-DP guarantees
- **Epsilon tracking** published to Kafka for audit

### ✅ Real-Time Streaming Pipeline
- **Apache Kafka** backbone with 6 topics:
  - `network_data`: Raw flow telemetry
  - `anomalies`: Detector outputs
  - `attack_classified`: Threat labels
  - `attack_predicted`: GNN forecasts
  - `alerts`: High-severity notifications
  - `fl_events`: FL round metrics
- **Event schemas** in `src/streaming/event_models.py`

### ✅ Production-Ready API & Dashboard
- **FastAPI backend**: REST + WebSocket (live event push)
- **PostgreSQL persistence**: Alerts, classifications, FL metrics
- **React/Next.js dashboard**: Real-time threat feed, FL health, attack timeline

---

## Development Workflow

### Run Locally (Without Docker)
```bash
# 1. Create virtualenv
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Start Kafka + Postgres (via Docker)
docker compose up kafka postgres -d

# 3. Override Kafka address for local services
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# 4. Run services individually
python services/network_simulator/main.py
python services/anomaly_lstm/main.py
python run_server.py
python run_client.py --client-id 0 --model-type lstm_autoencoder
```

### Run FL Simulation (No Kafka Required)
```bash
python simulate_federated_learning.py --model-type lstm_autoencoder --num-rounds 3
```

### Run Tests
```bash
pytest test_setup.py
cd dashboard/backend && pytest  # Backend API tests
```

---

## Configuration

All services read from environment variables. Copy `.env.example` → `.env` and customize:

| Variable | Default | Purpose |
|----------|---------|---------|
| `KAFKA_BOOTSTRAP_SERVERS` | `kafka:9092` | Kafka broker address |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection |
| `FLOWER_SERVER_ADDRESS` | `flower-server:8080` | FL server endpoint |
| `FL_NUM_ROUNDS` | `5` | Federated learning rounds |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Dashboard API URL |

See `.env.example` for full list.

---

## Known Issues & Limitations

### 🚧 Current State
- ✅ Core FL + streaming pipeline works
- ✅ All microservices containerized
- ⚠️ **Duplicate dashboard implementations** (Vite in root + Next.js in `dashboard/frontend/`)
- ⚠️ **Duplicate FastAPI backends** (`services/fastapi_backend/` + `dashboard/backend/`)
- ⚠️ Severity predictor uses weighted scoring, not actual Graph Neural Networks
- ⚠️ No authentication/authorization
- ⚠️ Secrets hardcoded in `docker-compose.yml`
- ⚠️ No CI/CD pipelines
- ❌ Neo4j integration incomplete
- ❌ IoTDB time-series storage not implemented

### 📋 Recommended Cleanup Actions
1. **Choose one dashboard**: Retire either Vite or Next.js version
2. **Choose one backend**: Consolidate `services/fastapi_backend/` and `dashboard/backend/`
3. **Add authentication**: JWT tokens, API keys
4. **Externalize secrets**: Use Docker secrets or Vault
5. **Add integration tests**: End-to-end pipeline validation
6. **Implement actual GNN**: Replace mock predictor with real graph neural network

---

## Contributing

This is a research prototype. Contributions welcome for:
- Real ICS/SCADA dataset integration
- Improved threat classification models
- Actual GNN-based prediction
- Security hardening (TLS, authn/authz)
- Performance optimization

---

## License

[Specify your license here]

---

## Citation

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

## Acknowledgments

Built with:
- [Flower](https://flower.dev/) - Federated Learning Framework
- [Apache Kafka](https://kafka.apache.org/) - Event Streaming
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API Framework
- [TensorFlow](https://www.tensorflow.org/) - Deep Learning
- [scikit-learn](https://scikit-learn.org/) - Machine Learning

---

**Status**: 🚧 Active Development | **Maturity**: Research Prototype  
**Last Updated**: November 2025
