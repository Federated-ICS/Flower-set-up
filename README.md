# Federated Network Attack Detection System

An end-to-end reference platform that blends Kafka streaming, federated anomaly detection, differential privacy, FastAPI, PostgreSQL, and a React dashboard to monitor attacks across distributed networks.

## Highlights

- **Kafka Backbone** – topics `network_data`, `anomalies`, `attack_classified`, `attack_predicted`, `alerts`, `fl_events`.
- **Streaming Analytics** – LSTM autoencoder, Isolation Forest, physics/rule engines, threat classifier, and a GNN-style predictor all operate as discrete microservices.
- **Flower Federated Learning** – server + three DP-enabled clients exchange gradients and publish round metrics to Kafka.
- **FastAPI + PostgreSQL** – Kafka ingestion, persistence, REST collections, and WebSocket fan-out for real-time UX.
- **React Dashboard** – Vite-powered UI renders anomaly feeds, classifier verdicts, predictor insights, alerts, and FL health.
- **Docker Compose** – turnkey orchestration for the full stack (Kafka/ZooKeeper, Postgres, analytics microservices, FL, backend, dashboard).

## Repository Layout

```
├── docker-compose.yml                 # full stack orchestrator
├── docker/python-service.Dockerfile   # base image for Python microservices
├── docs/ARCHITECTURE.md               # Kafka topics & service responsibilities
├── run_server.py / run_client.py      # Flower entrypoints (still usable locally)
├── services/
│   ├── network_simulator              # network_data producer
│   ├── anomaly_{lstm,iforest,physics} # anomaly detector microservices
│   ├── threat_classifier              # aggregates anomalies -> attack_classified
│   ├── gnn_predictor                  # attack_predicted + alerts
│   └── fastapi_backend                # FastAPI app + Dockerfile
├── src/
│   ├── client / server                # Flower implementations
│   ├── streaming                      # Kafka utils, event schemas, DP publisher
│   ├── data / models                  # synthetic data + detectors
│   └── streaming/services             # service base classes
└── dashboard/                         # Vite React dashboard
```

## Quick Start

1. **Prerequisites**
   - Docker + Docker Compose
   - ~8 GB RAM free (TensorFlow + Kafka brokers)

2. **Launch everything**
   ```bash
   docker compose up --build
   ```

3. **Interact**
   - Flower server: `localhost:8080`
   - FastAPI REST: `http://localhost:8000` (`/anomalies`, `/classifications`, `/predictions`, `/alerts`, `/fl-events`)
   - FastAPI WebSocket: `ws://localhost:8000/ws/events`
   - React dashboard: `http://localhost:4173`
   - PostgreSQL: `postgres://postgres:postgres@localhost:5432/attacks`

4. **Tear down**
   ```bash
   docker compose down
   ```

## Service Overview

| Service | Role | Produces | Consumes |
| --- | --- | --- | --- |
| `network-simulator` | Emits normalized flows derived from synthetic datasets | `network_data` | – |
| `anomaly-lstm` | TensorFlow LSTM autoencoder scoring | `anomalies` | `network_data` |
| `anomaly-iforest` | Isolation Forest detector | `anomalies` | `network_data` |
| `anomaly-physics` | Deterministic surge/impossible-port rules | `anomalies` | `network_data` |
| `threat-classifier` | Aggregates anomalies into attack labels | `attack_classified` | `anomalies` |
| `gnn-predictor` | Heuristic graph predictor + alerting | `attack_predicted`, `alerts` | `attack_classified` |
| `flower-server` | FedAvg orchestrator + Kafka FL metrics | `fl_events` | Flower RPC |
| `fl-client-{0,1,2}` | DP-enabled Flower clients | `fl_events` | Flower RPC |
| `fastapi-backend` | Consumes Kafka, persists to Postgres, exposes REST/WebSocket | – | all Kafka topics |
| `dashboard` | React UI | – | FastAPI REST/WebSocket |

## Flower + Differential Privacy

`src/client/flower_client.py` augments Flower `NumPyClient` with:

- **Gaussian noise** + clipping per weight tensor.
- **Budget tracking** (epsilon, delta) per client.
- **Kafka round logging** (role `client`, `node_id`, metrics, DP metadata) via `streaming.fl_events.RoundMetricPublisher`.

`src/server/flower_server.py` swaps the default strategy for `KafkaFedAvg`, which publishes aggregated fit/eval metrics each round back to Kafka on `fl_events`.

## FastAPI Backend

Located in `services/fastapi_backend/app`:

- SQLAlchemy models mirror Kafka payloads.
- `KafkaIngestor` (aiokafka) persists events and broadcasts updates to any WebSocket listeners.
- REST collections (latest 50 records) for anomalies, classifications, predictions, alerts, and FL events.
- WebSocket endpoint `/ws/events` streaming live payloads to the dashboard.

## React Dashboard

`dashboard/` uses Vite + React 18:

- Polls REST endpoints every 10 seconds for historical views.
- Subscribes to `/ws/events` for real-time updates.
- Sections: anomaly table, classifier votes, GNN severity feed, alert strip, FL health cards, live stream log.

## Developing Locally

- **Python tooling** – install `requirements.txt`, ensure Kafka/Postgres reachable, run Flower scripts directly (`python run_server.py` / `python run_client.py ...`).
- **FastAPI** – `uvicorn services.fastapi_backend.app.main:app --reload`.
- **Dashboard** – `cd dashboard && npm install && npm run dev`.

Env vars such as `KAFKA_BOOTSTRAP_SERVERS`, `DATABASE_URL`, and `VITE_API_BASE_URL` allow you to point components to external infrastructure when not using Docker Compose.

## References

- Architecture deep-dive: `docs/ARCHITECTURE.md`
- Synthetic data/model utilities: `src/data`, `src/models`
- Test harness: `python test_setup.py`

## Documentation

This repository glues several subsystems together; the high-level narrative below helps reason about data flow end to end.

### Event Contracts

`src/streaming/event_models.py` defines Pydantic-style dataclasses describing every Kafka payload (e.g., `NetworkPacket`, `AnomalyEvent`, `AttackClassification`, `AttackPrediction`, `AlertEvent`, `FLEvent`). All microservices serialize these models to JSON, ensuring schema alignment. `streaming/kafka_config.py` centralizes topic names, while `streaming/kafka_utils.py` offers shared producer/consumer helpers.

### Streaming Services

Under `services/` each microservice inherits from `streaming/services/base_service.py` to manage Kafka lifecycle:

1. `network_simulator` → publishes synthetic `NetworkPacket`s to `network_data`.
2. `anomaly_{lstm,iforest,physics}` → consume flows, run model/rule scoring, emit `AnomalyEvent`s.
3. `threat_classifier` → aggregates anomaly votes per flow and emits `AttackClassification` messages.
4. `gnn_predictor` → creates GNN-inspired severity forecasts (`AttackPrediction`) and escalates to the `alerts` topic.

Every service lives in its own folder with a `main.py` entrypoint suitable for Docker.

### Federated Learning + Differential Privacy

- `src/server/flower_server.py` swaps default FedAvg with `KafkaFedAvg`, so aggregated fit/eval results get published as `FLEvent`s via `RoundMetricPublisher`.
- `src/client/flower_client.py` extends `NumPyClient` with DP clipping/noising and per-round Kafka logging (client metrics, epsilon, delta). Clients can be run standalone (`run_client.py`) or via Compose (`fl-client-*` services).

### Backend Persistence & APIs

`services/fastapi_backend/app` contains:

- SQLAlchemy models mirroring Kafka events (`models.py`).
- `KafkaIngestor` consuming topics asynchronously and persisting to Postgres while rebroadcasting updates to WebSocket listeners.
- REST endpoints for historical queries and `/ws/events` for real-time streaming. Dockerfile + requirements are scoped to this service for lightweight deployments.

### Dashboard

`dashboard/` is a Vite React app polling the REST endpoints for historical snapshots and subscribing to the WebSocket for live updates. Components render anomaly tables, classifier verdicts, predictor explanations, alert feeds, FL statistics, and a raw event tail.

### Orchestration

`docker-compose.yml` bootstraps the entire environment (Kafka/ZooKeeper, Postgres, analytics services, FastAPI backend, Flower server/clients, dashboard). `docker/python-service.Dockerfile` is a base image for all Python microservices so you only maintain one dependency spec (`requirements.txt`). Service-specific Dockerfiles live alongside their code when they diverge (e.g., the FastAPI backend and dashboard).

For a conceptual overview of all pieces—including topic descriptions and service responsibilities—read `docs/ARCHITECTURE.md`.
