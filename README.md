# Federated Network Attack Detection Platform

A reference implementation that streams synthetic network traffic through a Kafka backbone, scores it with multiple anomaly/attack detectors, aggregates the results with a FastAPI backend and PostgreSQL, and visualizes everything in a Vite React dashboard. Flower federated learning coordinates three differential-privacy-aware clients, and all services are wired together with Docker Compose for a turn-key demo.

## What lives in this repo
- **Streaming microservices** under `services/`: network simulator, anomaly detectors (LSTM, Isolation Forest, physics rules), threat classifier, GNN-inspired predictor, and a FastAPI backend.
- **Federated learning** code in `src/`: Flower server and clients, Kafka publishing utilities, and supporting data/model helpers.
- **Dashboard** in `dashboard/`: Vite + React UI for historical queries and live updates.
- **Orchestration** via `docker-compose.yml` and a shared Python base image in `docker/python-service.Dockerfile`.
- **Docs and utilities**: architecture notes in `docs/ARCHITECTURE.md`, simulation helpers like `simulate_federated_learning.py`, and ad-hoc setup scripts.

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

## Architecture overview

### Streaming data plane
| Topic | Producers | Consumers | Purpose |
| --- | --- | --- | --- |
| `network_data` | `services/network_simulator` | `services/anomaly_*` | Normalized flow telemetry (10-D feature vector + metadata) |
| `anomalies` | `services/anomaly_lstm`, `services/anomaly_iforest`, `services/anomaly_physics` | `services/threat_classifier`, FastAPI backend | Detector scores + decision context |
| `attack_classified` | `services/threat_classifier` | `services/gnn_predictor`, FastAPI backend | Attack-type probabilities + supporting detectors |
| `attack_predicted` | `services/gnn_predictor` | FastAPI backend | GNN-style severity/next-hop forecasts |
| `alerts` | `services/gnn_predictor`, FastAPI backend | Dashboard, downstream SOAR hooks | Human-readable alert summaries |
| `fl_events` | Flower server & clients | FastAPI backend, dashboard | Round metrics, DP budgets, client health |

Kafka bootstrap defaults to `kafka:9092` but can be overridden via `KAFKA_BOOTSTRAP_SERVERS`. Payload schemas live in `src/streaming/event_models.py` so every service shares the same contract.

### Detection & analytics services (`services/`)
- `network_simulator`: wraps `src/data/data_generation.py` to stream synthetic traffic into `network_data`.
- `anomaly_lstm`: packages `LSTMAutoencoderDetector` for real-time scoring with reconstruction-error thresholds.
- `anomaly_iforest`: boots an `IsolationForestDetector`, exposes decision scores, and emits JSON anomaly events.
- `anomaly_physics`: deterministic safety/physics rules (payload surge, impossible ports) to provide fast guards.
- `threat_classifier`: aggregates anomaly votes per flow and labels attacks (benign/probe/DoS) before handing off.
- `gnn_predictor`: ingests classifier outputs, approximates a graph attention model, and raises high-severity alerts.

### Federated learning loop (`src/` + root scripts)
- `run_server.py` spins up the Flower server (`src/server/flower_server.py`) with FedAvg + Kafka metric publishing.
- `run_client.py` instantiates `AnomalyDetectorClient` (Isolation Forest or LSTM) per site, adds optional DP noise, and can run standalone or as `docker-compose` services `fl-client-0/1/2`.
- `simulate_federated_learning.py` lets you dry-run client/server logic without Kafka, useful for CI smoke tests.
- All Flower entities publish progress via `RoundMetricPublisher` into the `fl_events` topic so the backend/dashboard can track accuracy, loss, epsilon, etc.

### API + persistence + dashboard
- `services/fastapi_backend`: FastAPI app with Kafka consumers, PostgreSQL persistence (`postgres://postgres:postgres@postgres:5432/attacks`), REST routes, and WebSocket fan-out.
- `dashboard/`: Vite + React UI consuming REST for history and `ws://.../ws/events` for live updates (anomalies, classifications, predictions, FL rounds).
- Database migrations/DDL live alongside the backend service; default Docker stack provisions Postgres storage via the `pgdata` volume.

### Orchestration & operations
- `docker-compose.yml` starts the complete topology: Zookeeper/Kafka, Postgres, Flower server + clients, simulators, detectors, classifier, predictor, FastAPI backend, and dashboard.
- `docker/python-service.Dockerfile` is the shared base image (Python 3.10 + repo requirements) used by every Python service, guaranteeing consistent dependencies.
- Environment overrides (`KAFKA_BOOTSTRAP_SERVERS`, `DATABASE_URL`, `SERVER_ADDRESS`, etc.) can be applied per container via Compose or `.env` files.

For deeper diagrams and future-state notes (Neo4j, IoTDB, etc.), refer to `docs/ARCHITECTURE.md`.

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

## Developing without Docker
### Python services (Flower + streaming microservices)
1. Create a virtualenv and install shared deps:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Point services to your infrastructure with env vars (or rely on defaults):
   - `KAFKA_BOOTSTRAP_SERVERS` (e.g., `localhost:29092`)
   - `DATABASE_URL` (e.g., `postgresql+psycopg2://postgres:postgres@localhost:5432/attacks`)
3. Run individual services (examples):
   ```bash
   python services/network_simulator/main.py
   python services/anomaly_lstm/main.py
   python run_server.py                 # Flower server
   python run_client.py --node-id 0     # Flower client (repeat for 1,2)
   ```

### FastAPI backend
1. Move into the service directory and install its specific requirements if needed (already covered by the root `requirements.txt`):
   ```bash
   uvicorn services.fastapi_backend.app.main:app --reload
   ```
2. REST and WebSocket endpoints mirror the Compose setup (port 8000 by default). SQLite is used automatically for backend tests; PostgreSQL is expected in production.

### React dashboard
1. Install dependencies and start the dev server:
   ```bash
   cd dashboard
   npm install
   npm run dev -- --host
   ```
2. Override the backend base URL if it is not `http://localhost:8000`:
   ```bash
   VITE_API_BASE_URL=http://your-backend:8000 npm run dev -- --host
   ```

## Running tests
- Backend pytest configuration defaults to a local SQLite database with foreign key enforcement (no Postgres needed for unit tests).
- Execute the test suite from the repo root (ensure Python deps are installed):
  ```bash
  PYENV_VERSION=3.11.12 python -m pytest
  ```

## Helpful tips
- Kafka topic names and data schemas are centralized in `src/streaming`.
- Each microservice folder under `services/` contains a `main.py` entrypoint suitable for Docker or local runs.
- `simulate_federated_learning.py` can be used to run a lightweight FL simulation without Kafka/PostgreSQL.
- For an architecture walkthrough and data-flow diagrams, see `docs/ARCHITECTURE.md`.

Happy hacking!
