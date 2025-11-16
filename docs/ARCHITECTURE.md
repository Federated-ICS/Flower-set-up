# Federated Network Attack Detection Architecture

The platform stitches together federated learning, classic anomaly detectors, rule engines, and graph-based threat prediction over a Kafka-centric event spine. Every component exchanges structured events so that new analytics or automations can subscribe without rewriting ETL glue.

## Kafka Streaming Backbone

| Topic | Producer(s) | Consumer(s) | Payload |
| --- | --- | --- | --- |
| `network_data` | `network-simulator` | all anomaly detectors | Raw/normalized network flow samples |
| `anomalies` | `anomaly-lstm`, `anomaly-iforest`, `anomaly-physics` | `threat-classifier`, FastAPI | Detector id, score, rich context |
| `attack_classified` | `threat-classifier` | `gnn-predictor`, FastAPI | Attack type probabilities |
| `attack_predicted` | `gnn-predictor` | FastAPI | GNN severity/next-hop predictions |
| `fl_events` | Flower server & DP clients | FastAPI, dashboard | Round metrics, per-client noise budget |
| `alerts` | `gnn-predictor`, FastAPI | Dashboard, downstream SOAR | Human-friendly alert summaries |

All services resolve the Kafka bootstrap server via `KAFKA_BOOTSTRAP_SERVERS` (default `kafka:9092`) and share Avro-like JSON envelopes defined in `src/streaming/event_models.py`.

## Microservices

- **Network Simulator** – generates synthetic flows leveraging `src/data/data_generation.py`. Publishes to `network_data`.
- **Anomaly Detectors** – three independent deployments:
  - `anomaly-lstm`: wraps `LSTMAutoencoderDetector`, warm-starts from checkpoints when available.
  - `anomaly-iforest`: wraps `IsolationForestDetector`.
  - `anomaly-physics`: lightweight rule engine (e.g., surge detection, impossible travel) for deterministic baselines.
  Each service consumes `network_data`, batches windows, scores, and publishes anomaly finding events to `anomalies`.
- **Threat Classifier** – aggregates anomalies into attack verdicts using a scikit-learn logistic regression baseline, publishing structured outputs to `attack_classified`.
- **GNN Predictor** – stands in for a spatio-temporal GNN by learning node embeddings from anomalies, producing severity forecasts on `attack_predicted` and auto-escalating high-risk situations into `alerts`.

## Federated Learning Layer

- **Flower Server** – the orchestrator uses the FedAvg strategy with custom metric aggregation. Every round, `RoundMetricPublisher` emits payloads to `fl_events`.
- **DP Clients** – three Flower NumPy clients extend `AnomalyDetectorClient` with per-update Gaussian noise via Opacus-style gradient sanitizers. Each client also publishes local round metrics to Kafka (tagged with logical client ids rather than hostnames).
- **DP Accounting** – clients track epsilon deltas and surface budgets through the same Kafka payloads so downstream systems (FastAPI + dashboard) can report FL health.

## FastAPI Backend

The backend owns:

1. **Kafka ingestion** – asynchronous consumers push `network_data`, `anomalies`, `attack_classified`, `attack_predicted`, `alerts`, and `fl_events` into PostgreSQL tables via SQLAlchemy models.
2. **REST API** – endpoints for current anomalies, attack classifications, predictions, alert feed, and FL round metrics.
3. **WebSockets** – Fan-out of live events to the React dashboard without browser-managed Kafka clients.

## React Dashboard

A Vite-powered React app renders:

- Realtime anomaly stream with filtering by detector and host.
- Attack classifier probabilities (stacked bars).
- GNN predictor insights (graph of node risk, severity sparkline, textual next-hop forecast).
- Federated learning health (round timeline, client DP budgets, accuracy trends).

Dashboard data originates from FastAPI REST for historical views and WebSocket push for live updates.

## Docker Compose Orchestration

`docker-compose.yml` wires:

- **Infrastructure**: Zookeeper, Kafka, PostgreSQL, pgAdmin.
- **Analytics**: network simulator, three anomaly detectors, threat classifier, GNN predictor.
- **Federated Learning**: Flower server + three DP clients.
- **Application**: FastAPI backend, React dashboard.

Each container shares `.env` defaults (Kafka bootstrap, Postgres creds, Flower server URI). The `Makefile` (optional) or direct compose commands spin the full stack locally.
