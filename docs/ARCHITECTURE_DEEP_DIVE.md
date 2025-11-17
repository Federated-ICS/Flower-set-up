# FedICS Architecture Deep Dive

## System Purpose

**FedICS** (Federated ICS Security) is a streaming-first network intrusion detection system designed for distributed industrial control systems (ICS) and critical infrastructure. It detects, classifies, and predicts cyber attacks while preserving data privacy through federated learning.

**Key Innovation**: Multiple detection sites (e.g., power plants, water treatment facilities) can collaboratively train machine learning models **without sharing raw operational data**, only exchanging encrypted model updates.

---

## Component Inventory

### Layer 1: Data Generation (`src/data/`)
| Component | Purpose | Key Functions |
|-----------|---------|---------------|
| `data_generation.py` | Generates synthetic network traffic with labeled anomalies | `generate_dataset()`, `split_data_for_clients()` |

**What it does**:
- Creates 10-dimensional feature vectors (normal + anomalous)
- Normal data: Gaussian distribution (mean=0, std=1)
- Anomalous data: Shifted mean (5) and higher variance (3x)
- Splits data across 3 federated clients (simulating different facilities)

---

### Layer 2: Anomaly Detection Models (`src/models/`)

#### LSTM Autoencoder (`lstm_autoencoder_detector.py`)
**Purpose**: Temporal behavior analysis

**Architecture**:
```
Input (10 features) → LSTM Encoder (5 latent dims) 
→ RepeatVector → LSTM Decoder → Output (10 features)
```

**Detection Logic**:
- Trains to reconstruct normal behavior
- Computes Mean Squared Error (MSE) between input/output
- Anomaly if MSE > 95th percentile threshold

**Use Case**: Detecting slow-drift attacks, behavioral changes

#### Isolation Forest (`isolation_forest_detector.py`)
**Purpose**: Point anomaly detection

**Algorithm**:
- Decision tree ensemble (100 trees)
- Isolates outliers with fewer splits
- Contamination parameter: 10% (expects 10% anomalies)

**Use Case**: Detecting sudden spikes, rare events

---

### Layer 3: Streaming Services (`services/`)

#### Network Simulator (`services/network_simulator/`)
**Purpose**: Traffic generator

**Behavior**:
- Generates 1000 synthetic flows (900 normal, 100 anomalous)
- Publishes to Kafka topic `network_data` every 0.5 seconds
- Includes IP addresses, ports, protocol, payload size
- Cycles through dataset infinitely

**Output Schema** (`NetworkPacket`):
```json
{
  "event_type": "network_packet",
  "flow_id": "uuid",
  "src_ip": "192.168.1.10",
  "dst_ip": "10.0.0.1",
  "protocol": "tcp",
  "src_port": 5000,
  "dst_port": 80,
  "payload_size": 1024.5,
  "features": [0.12, -0.45, ...],  // 10-D vector
  "metadata": {"label": "0"},      // 0=normal, 1=anomaly
  "created_at": "2025-11-17T10:30:00Z"
}
```

#### Anomaly Detectors (`services/anomaly_{lstm,iforest,physics}/`)
**Purpose**: Score flows for anomalies

**Process**:
1. Consume from `network_data`
2. Extract 10-D feature vector
3. Run model inference
4. Publish to `anomalies` topic

**Output Schema** (`AnomalyEvent`):
```json
{
  "event_type": "anomaly",
  "detector": "anomaly_lstm",
  "flow_id": "uuid",
  "score": 0.87,          // Confidence/severity
  "is_anomaly": true,
  "features": [...],
  "context": {
    "threshold": "0.62",
    "mse": "0.87"         // Detector-specific metadata
  },
  "created_at": "2025-11-17T10:30:01Z"
}
```

**Physics Rules Engine**:
- Deterministic rules (no ML):
  - Surge detection: `payload_size > 8000` or `||features|| > 25`
  - Impossible port: `src_port < 1024 AND dst_port < 1024`
- Executes in <1ms (fast baseline)

#### Threat Classifier (`services/threat_classifier/`)
**Purpose**: Aggregate anomaly votes into attack labels

**Algorithm**:
- Maintains sliding window of last 5 anomaly events per flow
- Triggers when ≥2 detectors vote "anomaly"
- Classifies based on average score:
  - `avg_score > 12` → **DoS** (Denial of Service)
  - `avg_score > 6` → **Probe** (Reconnaissance)
  - `otherwise` → **Benign**

**Output Schema** (`AttackClassification`):
```json
{
  "event_type": "attack_classification",
  "classifier": "threat_classifier",
  "flow_id": "uuid",
  "label": "dos",
  "probabilities": {
    "dos": 0.85,
    "probe": 0.12,
    "benign": 0.03
  },
  "supporting_detectors": ["anomaly_lstm", "anomaly_iforest"],
  "created_at": "2025-11-17T10:30:02Z"
}
```

#### Severity Predictor (`services/gnn_predictor/`)
**Purpose**: Forecast attack severity and next hop

**Current Implementation** (⚠️ Not actually a GNN):
- Weighted scoring: `severity = 0.6*P(dos) + 0.4*P(probe) + random[0,0.15]`
- Generates alert if `severity > 0.65`
- "Next hop" = destination IP (placeholder logic)

**Future Enhancement**: Replace with Graph Attention Network (GAT) using ATT&CK graph

**Output Schema** (`AttackPrediction`):
```json
{
  "event_type": "attack_prediction",
  "predictor": "gnn_predictor",
  "flow_id": "uuid",
  "severity": 0.78,
  "impacted_nodes": ["192.168.1.10", "10.0.0.1"],
  "next_hop": "10.0.0.1",
  "explanation": "Combined anomaly votes -> dos.",
  "created_at": "2025-11-17T10:30:03Z"
}
```

**Alert Schema** (`AlertEvent` — published to `alerts` topic):
```json
{
  "event_type": "alert",
  "flow_id": "uuid",
  "title": "High severity attack forecast",
  "severity": "high",     // or "medium", "low"
  "summary": "GNN forecast severity 0.78 (dos)",
  "source": "gnn_predictor",
  "payload": {"probabilities": "..."},
  "created_at": "2025-11-17T10:30:03Z"
}
```

---

### Layer 4: Federated Learning (`src/server/`, `src/client/`)

#### Flower Server (`src/server/flower_server.py`)
**Purpose**: Orchestrate federated training rounds

**Strategy**: FedAvg (Federated Averaging)
- Aggregates model weights from clients
- Weighted average based on client dataset sizes
- Runs for 5 rounds by default

**Metrics Aggregation**:
- Collects accuracy, precision, recall, F1 from each client
- Computes weighted average across clients
- Logs aggregated metrics per round

**Configuration**:
```python
FedAvg(
    fraction_fit=1.0,          # Use all clients for training
    fraction_evaluate=1.0,      # Use all clients for eval
    min_fit_clients=3,          # Minimum clients per round
    min_evaluate_clients=3,
    min_available_clients=3,
    evaluate_metrics_aggregation_fn=weighted_average,
    fit_metrics_aggregation_fn=weighted_average,
)
```

#### Flower Clients (`src/client/flower_client.py`)
**Purpose**: Train models locally, share updates with server

**Process**:
1. Receive global model weights from server
2. Train on local data partition
3. Send updated weights back to server
4. Evaluate on local test set

**Differential Privacy** (⚠️ Partially implemented):
- Gradient clipping (max norm)
- Gaussian noise addition
- Epsilon (ε) tracking for privacy budget
- **Gap**: No formal DP library integration (Opacus, TensorFlow Privacy)

**FL Event Publishing**:
- Each client publishes round metrics to `fl_events` topic
- Includes: `round_id`, `node_id`, `accuracy`, `loss`, `epsilon`, `delta`

**FL Event Schema** (`FLEvent`):
```json
{
  "event_type": "fl_event",
  "round_id": 3,
  "role": "client",       // or "server"
  "node_id": "client_0",
  "accuracy": 0.94,
  "precision": 0.91,
  "recall": 0.88,
  "f1_score": 0.89,
  "loss": 0.23,
  "epsilon": 1.5,         // Privacy budget consumed
  "delta": 1e-5,
  "extra": {},
  "created_at": "2025-11-17T10:35:00Z"
}
```

---

### Layer 5: Backend API (`services/fastapi_backend/`)

#### FastAPI Application (`app/main.py`)
**Purpose**: REST API + WebSocket server

**Endpoints**:
- `GET /anomalies` — Query anomaly events
- `GET /classifications` — Query attack classifications
- `GET /predictions` — Query attack predictions
- `GET /alerts` — Query alerts
- `GET /fl-events` — Query FL round metrics
- `GET /docs` — Auto-generated API documentation
- `WS /ws/events` — WebSocket for live event streaming

#### Kafka Ingestor (`app/kafka_ingestor.py`)
**Purpose**: Consume Kafka topics → PostgreSQL

**Background Task**:
- Runs async consumers for all 6 topics
- Parses JSON events
- Inserts into PostgreSQL tables via SQLAlchemy ORM
- Broadcasts new events to WebSocket clients

**Database Schema** (PostgreSQL):
```sql
-- Simplified representation
TABLE anomalies (
    id SERIAL PRIMARY KEY,
    detector VARCHAR,
    flow_id VARCHAR,
    score FLOAT,
    is_anomaly BOOLEAN,
    features JSON,
    context JSON,
    created_at TIMESTAMP
);

TABLE attack_classifications (...);
TABLE attack_predictions (...);
TABLE alerts (...);
TABLE fl_events (...);
```

#### WebSocket Manager
**Purpose**: Push real-time events to dashboard

**Behavior**:
- Clients connect to `/ws/events`
- Server broadcasts every new event (anomalies, alerts, FL metrics)
- JSON messages pushed without polling

---

### Layer 6: Dashboard (`dashboard/`)

⚠️ **Duplicate Implementations Detected**:
1. **Vite + React** (`dashboard/src/`, `dashboard/index.html`)
   - Simple prototype
   - Basic anomaly/alert display
   
2. **Next.js + TypeScript** (`dashboard/frontend/`)
   - Production-ready
   - Multiple pages: Alerts, Attack Graph, FL Status
   - Rich components (charts, graphs, tables)
   - WebSocket integration

**Recommendation**: **Consolidate to Next.js** (more complete)

#### Key Pages (Next.js):
- `/` — Dashboard home (system status, recent alerts)
- `/alerts` — Alert table with filtering
- `/attack-graph` — ATT&CK technique visualization
- `/fl-status` — Federated learning health (rounds, clients, DP budgets)

---

## Data Flow Diagram

### Main Pipeline (Attack Detection)
```
┌─────────────────────┐
│ Network Simulator   │
│ (synthetic traffic) │
└──────────┬──────────┘
           │
           ▼ Kafka: network_data
┌───────────────────────────────────────────┐
│ Anomaly Detectors (Parallel Processing)  │
│  ┌──────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ LSTM         │  │ IForest    │  │ Physics  │ │
│  │ Autoencoder  │  │ (tree)     │  │ Rules    │ │
│  └──────────────┘  └────────────┘  └──────────┘ │
└──────────┬────────────────────────────────┘
           │
           ▼ Kafka: anomalies
┌─────────────────────┐
│ Threat Classifier   │
│ (vote aggregation)  │
└──────────┬──────────┘
           │
           ▼ Kafka: attack_classified
┌─────────────────────┐
│ Severity Predictor  │
│ (weighted scoring)  │
└──────────┬──────────┘
           │
           ├─▶ Kafka: attack_predicted
           └─▶ Kafka: alerts (if severe)
           │
           ▼
┌─────────────────────┐
│ FastAPI Backend     │
│  • Kafka Consumer   │
│  • PostgreSQL       │
│  • WebSocket Push   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ React/Next.js       │
│ Dashboard           │
│  • Live alerts      │
│  • Attack timeline  │
│  • FL health        │
└─────────────────────┘
```

### Federated Learning Loop (Parallel to Main Pipeline)
```
┌──────────────────┐
│ Flower Server    │
│ (FedAvg)         │
└────────┬─────────┘
         │
         ├─────────────────────────┐
         │                         │
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│ Client 0        │       │ Client 1/2      │
│ • Local data    │       │ • Local data    │
│ • Train LSTM    │       │ • Train models  │
│ • DP noise      │       │ • DP noise      │
└────────┬────────┘       └────────┬────────┘
         │                         │
         └────────┬────────────────┘
                  │
                  ▼ Kafka: fl_events
         ┌────────────────┐
         │ FastAPI Backend│
         │ (FL metrics)   │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Dashboard      │
         │ (FL Status)    │
         └────────────────┘
```

---

## Kafka Topics & Event Schemas

| Topic | Schema | Producers | Consumers | Retention |
|-------|--------|-----------|-----------|-----------|
| `network_data` | `NetworkPacket` | network_simulator | anomaly_* | 1 hour |
| `anomalies` | `AnomalyEvent` | anomaly_lstm, anomaly_iforest, anomaly_physics | threat_classifier, backend | 24 hours |
| `attack_classified` | `AttackClassification` | threat_classifier | gnn_predictor, backend | 7 days |
| `attack_predicted` | `AttackPrediction` | gnn_predictor | backend | 7 days |
| `alerts` | `AlertEvent` | gnn_predictor, backend | dashboard, SOAR | 30 days |
| `fl_events` | `FLEvent` | flower_server, flower_clients | backend, dashboard | 30 days |

**Schema Definitions**: `src/streaming/event_models.py`

---

## Key Features

### ✅ Implemented
1. **Multi-Model Detection**
   - LSTM Autoencoder (temporal)
   - Isolation Forest (point anomalies)
   - Physics Rules (deterministic)

2. **Federated Learning**
   - Flower framework (FedAvg)
   - 3 distributed clients
   - Model weight aggregation
   - Metrics tracking

3. **Streaming Architecture**
   - Apache Kafka backbone
   - Event-driven microservices
   - Decoupled communication

4. **Real-Time Dashboard**
   - WebSocket push updates
   - Alert visualization
   - FL health monitoring

5. **Differential Privacy** (Partial)
   - Gradient clipping
   - Gaussian noise
   - Epsilon tracking

### ⚠️ Partially Implemented
1. **Differential Privacy**
   - ✅ Noise addition
   - ❌ Formal privacy accounting (RDP, moments accountant)
   - ❌ Integration with Opacus or TensorFlow Privacy

2. **Graph Neural Network**
   - ❌ No actual GNN architecture
   - ❌ No ATT&CK graph modeling
   - ✅ Placeholder severity scoring

3. **Authentication**
   - ❌ No JWT/OAuth
   - ❌ No API keys
   - ❌ No rate limiting

### ❌ Not Implemented
1. **Real Datasets**
   - Only synthetic data supported
   - No PCAP parsing
   - No Modbus/DNP3 decoders

2. **Neo4j Integration**
   - Mentioned in configs
   - Not wired to services

3. **IoTDB Integration**
   - Time-series storage planned
   - Not implemented

4. **CI/CD**
   - No automated testing
   - No deployment pipelines

5. **Monitoring**
   - No Prometheus metrics
   - No distributed tracing
   - No health checks

---

## Architectural Strengths

1. **Loose Coupling** — Kafka enables independent service development
2. **Horizontal Scalability** — Add more Kafka partitions/consumers
3. **Privacy by Design** — FL keeps data local
4. **Composable Detection** — Easy to add new detectors
5. **Real-Time Updates** — WebSocket push for low latency

---

## Architectural Weaknesses

1. **Duplicate Implementations**
   - 2 dashboards (Vite + Next.js)
   - 2 backends (`services/fastapi_backend/` + `dashboard/backend/`)

2. **Misleading Names**
   - "GNN predictor" doesn't use GNNs

3. **Incomplete Features**
   - DP implementation lacks formal accounting
   - No real datasets
   - No authentication

4. **Security Gaps**
   - Secrets in plaintext (`docker-compose.yml`)
   - No TLS for Kafka
   - No input validation

5. **Operational Gaps**
   - No health checks
   - No graceful shutdown
   - No monitoring/alerting

---

## Gaps & Risks

### High Priority
- **Security**: No authentication, hardcoded secrets
- **Duplicate Code**: Wasted development effort
- **DP Incomplete**: Privacy claims not formally verified

### Medium Priority
- **Testing**: No integration tests
- **Documentation**: Missing API docs, deployment guide
- **Monitoring**: No observability

### Low Priority
- **GNN**: Not using real graph neural networks
- **Real Data**: Synthetic only
- **Neo4j/IoTDB**: Planned but not integrated

---

## Recommended Next Steps

1. **Week 1**: Consolidate dashboards & backends
2. **Week 2**: Add `.env` configuration, remove secrets from code
3. **Week 3**: Implement authentication (JWT)
4. **Week 4**: Add integration tests
5. **Future**: Real GNN, real datasets, production deployment

---

## Project Naming Recommendation

**Current**: Flower-set-up (generic)

**Recommended**: **FedICS** (Federated ICS Security)
- Clear domain focus
- Professional
- Searchable
- Memorable

---

This architecture delivers a working proof-of-concept for federated anomaly detection but needs cleanup and hardening before production use. The core streaming + FL pipeline is sound; focus on consolidating duplicates and filling operational gaps.
