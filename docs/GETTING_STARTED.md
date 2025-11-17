# FedICS — Getting Started (A–Z)

This guide is for developers who are new to FedICS and want a **from-zero to running** path. It covers prerequisites, setup, running the full stack, and verifying that everything works.

## 1) Prerequisites
- **Docker & Docker Compose** (required for the all-in-one stack)
- **Python 3.11** (for running services locally without Docker)
- **Node.js 18+** (only if you plan to develop the dashboard locally)
- **Hardware**: ~8 GB RAM available for Kafka, PostgreSQL, and ML services

## 2) Clone and configure
```bash
git clone https://github.com/Federated-ICS/Flower-set-up.git
cd Flower-set-up

# Copy environment defaults
test -f .env || cp .env.example .env
```

> Tip: Most newcomers can keep the defaults. If you already have local Kafka/PostgreSQL instances, update `KAFKA_BOOTSTRAP_SERVERS` and `DATABASE_URL` inside `.env` to point to them.

## 3) Run the full stack with Docker Compose
The fastest path is the built-in setup target:
```bash
make setup
```
This will:
1) Ensure `.env` exists
2) Install Python dependencies
3) Build and start all containers
4) Run database migrations and seed sample data

Manual start (if you prefer explicit steps):
```bash
docker compose up --build
```

### What to expect once running
- **Dashboard**: http://localhost:3000
- **FastAPI docs**: http://localhost:8000/docs
- **Flower server**: http://localhost:8080
- **PostgreSQL**: postgres://postgres:postgres@localhost:5432/ics_threat_detection

### Quick health checks
```bash
make ps               # List running containers
make health           # Basic HTTP and database checks
make logs             # Follow all service logs
```

## 4) Daily workflow commands
- `make up` / `make down` — start/stop the stack in the background
- `make dev` — run with dev overrides (hot reload where supported)
- `make logs-backend` / `make logs-dashboard` / `make logs-fl` — tail specific components
- `make kafka-topics` — inspect Kafka topics; `make kafka-clear` resets them
- `make db-reset` — rebuild PostgreSQL data + rerun migrations

## 5) Run services locally (without Docker)
Use this mode if you want IDE debugging while keeping Kafka/PostgreSQL in Docker:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

docker compose up kafka postgres -d
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Start Python services one by one
python services/network_simulator/main.py
python services/anomaly_lstm/main.py
python services/anomaly_iforest/main.py
python services/anomaly_physics/main.py
python services/threat_classifier/main.py
python services/severity_predictor/main.py

# Flower server + clients
python run_server.py
python run_client.py --client-id 0 --model-type lstm_autoencoder
python run_client.py --client-id 1 --model-type lstm_autoencoder
python run_client.py --client-id 2 --model-type isolation_forest
```

## 6) Simulations and tests
- **Federated learning smoke test** (no Kafka required):
  ```bash
  python simulate_federated_learning.py --model-type lstm_autoencoder --num-rounds 3
  ```
- **Pytest smoke tests**:
  ```bash
  pytest test_setup.py -v
  ```

## 7) Troubleshooting essentials
- **Ports already in use**: Stop conflicting local services or change ports in `.env`.
- **Containers restarting**: Check `make logs` and confirm `.env` values (Kafka/PostgreSQL addresses) match what the services expect.
- **Dashboard empty**: Ensure the simulator, detectors, classifier, and predictor containers are running (`make ps`).
- **Slow builds**: Use `docker compose build --progress=plain` to get more detail; add `--no-cache` if dependency layers look stale.

## 8) Where to look in the codebase
- **`services/`** — Kafka microservices (simulator, detectors, classifier, predictor, FastAPI backend)
- **`src/`** — Flower server/clients, models, and streaming utilities
- **`dashboard/`** — Next.js UI for live alerts and FL metrics
- **`Makefile`** — Convenience targets for common tasks

You now have the full system running end-to-end. Explore the API at `/docs`, watch the live dashboard, and adjust configuration in `.env` as needed.
