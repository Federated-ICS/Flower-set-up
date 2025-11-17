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
