# Backend API Architecture
# Federated ICS Threat Detection System

Based on the architecture specifications from `Idea_and_architecture/` folder.

## Overview

This document defines the FastAPI backend architecture that implements the three-layer detection system with federated learning capabilities.

---

## System Architecture Principles

### 1. Three-Layer Detection System

```
Layer 1: Anomaly Detection (Unsupervised)
├── Isolation Forest (< 5 seconds)
└── LSTM Autoencoder (< 30 seconds)

Layer 2: Attack Classification (Supervised)
└── Neural Network Threat Classifier (< 2 seconds)

Layer 3: Attack Prediction (Graph-Based)
└── Graph Neural Network (< 10 seconds)
```

### 2. Context Buffer Architecture

**Purpose**: Store 60-second rolling window for temporal analysis

**Storage**: Redis (in-memory)
- Size: ~300KB per facility
- Duration: 60-second rolling window
- Shared by: LSTM Autoencoder + Threat Classifier

**Features Stored**:
- TCP: flags, ports, payload sizes, connection states
- HTTP: methods, content lengths, URIs, response codes
- DNS: query names, lengths, types, retransmissions
- Modbus: transaction IDs, unit IDs, message lengths
- MQTT: message types, topics, payload sizes

### 3. Event-Driven Architecture

**Message Bus**: Apache Kafka
- Topics: network_data, alerts, predictions, fl_events
- Pattern: Pub/Sub for async communication
- Consumers: Detection services, API gateway

---

## Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application entry
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connections
│   │
│   ├── api/                    # API routes
│   │   ├── __init__.py
│   │   ├── alerts.py           # Alert management endpoints
│   │   ├── fl_status.py        # Federated learning endpoints
│   │   ├── predictions.py      # Attack prediction endpoints
│   │   ├── context.py          # Context buffer endpoints
│   │   ├── demo.py             # Demo scenario endpoints
│   │   └── websocket.py        # WebSocket endpoint
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── alert.py
│   │   ├── fl_round.py
│   │   ├── prediction.py
│   │   └── network_data.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── alert.py
│   │   ├── fl_status.py
│   │   ├── prediction.py
│   │   └── context.py
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── kafka_consumer.py  # Kafka → WebSocket bridge
│   │   ├── websocket_manager.py
│   │   ├── context_buffer.py  # Redis context management
│   │   ├── alert_service.py
│   │   ├── fl_service.py
│   │   └── prediction_service.py
│   │
│   ├── repositories/           # Data access layer
│   │   ├── __init__.py
│   │   ├── alert_repository.py
│   │   ├── fl_repository.py
│   │   └── prediction_repository.py
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── dependencies.py     # FastAPI dependencies
│       └── helpers.py
│
├── scripts/                    # Setup scripts
│   ├── seed_database.py
│   ├── load_mitre_attack.py
│   └── check_services.py
│
├── tests/                      # Test files
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
│
├── alembic/                    # Database migrations
│   └── versions/
│
├── pyproject.toml              # Poetry dependencies
├── .env.example                # Environment template
└── README.md
```

---


## API Endpoints Specification

### Health & System

```
GET /health
Response: { status: "healthy", services: {...} }

GET /api/system/status
Response: {
  active_alerts: number,
  fl_progress: number,
  prediction_accuracy: number,
  facilities: Array<{ id, name, status }>
}
```

### Alerts API

```
GET /api/alerts
Query: severity, facility, status, search, page, limit
Response: {
  alerts: Alert[],
  total: number,
  page: number,
  pages: number
}

GET /api/alerts/{alert_id}
Response: Alert (with full context analysis)

PUT /api/alerts/{alert_id}/status
Body: { status: "acknowledged" | "resolved" | "false-positive" }
Response: Alert

GET /api/alerts/stats
Response: {
  total: number,
  critical: number,
  unresolved: number,
  false_positives: number
}
```

### Context Buffer API

```
GET /api/context/{facility_id}/current
Response: {
  facility_id: string,
  window_duration: "60 seconds",
  features: ContextFeatures,
  metrics: NetworkMetrics
}

GET /api/context/{alert_id}/evidence
Response: {
  alert_id: string,
  timeline: TimelinePoint[],
  evidence: Evidence,
  pattern_analysis: PatternAnalysis
}

GET /api/context/{alert_id}/timeline
Response: {
  timeline: Array<{
    time: string,
    packets_per_sec: number,
    unique_dest_ips: number,
    protocol_distribution: number,
    status: "normal" | "suspicious" | "attack"
  }>
}
```

### Federated Learning API

```
GET /api/fl/rounds/current
Response: FLRound (current round details)

GET /api/fl/rounds
Query: limit, offset
Response: { rounds: FLRound[], total: number }

GET /api/fl/rounds/{round_id}
Response: FLRound (with detailed metrics)

POST /api/fl/rounds/trigger
Response: { round_id: number, status: "started" }

GET /api/fl/clients
Response: FLClient[] (all facility clients)

GET /api/fl/clients/{client_id}
Response: FLClient (detailed client status)

GET /api/fl/privacy-metrics
Response: {
  epsilon: number,
  delta: string,
  data_size: string,
  encryption: string,
  privacy_budget_remaining: number
}
```

### Predictions API

```
GET /api/predictions
Query: limit, offset, validated
Response: { predictions: Prediction[], total: number }

GET /api/predictions/{prediction_id}
Response: Prediction (with validation status)

POST /api/predictions/predict
Body: { current_technique: string, alert_id: string }
Response: Prediction

GET /api/mitre/graph
Response: {
  nodes: Node[],
  links: Link[]
}

GET /api/mitre/technique/{technique_id}
Response: TechniqueDetails
```

### Demo API

```
POST /api/demo/scenarios/port-scan
Body: { facility_id: string }
Response: { scenario_id: string, status: "started" }

POST /api/demo/scenarios/fl-round
Response: { round_id: number, status: "started" }

POST /api/demo/scenarios/multi-stage
Body: { facility_id: string }
Response: { scenario_id: string, status: "started" }

GET /api/demo/status
Response: {
  active_scenarios: Scenario[],
  last_scenario: Scenario
}

POST /api/demo/reset
Response: { status: "reset_complete" }
```

### WebSocket

```
WS /ws
Channels: alerts, fl_status, predictions, system

Message Format:
{
  channel: "alerts" | "fl_status" | "predictions" | "system",
  type: "new" | "update" | "delete",
  data: {...}
}
```

---


## Data Models (SQLAlchemy)

### Alert Model

```python
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(UUID, primary_key=True)
    timestamp = Column(DateTime, nullable=False)
    facility_id = Column(String, nullable=False)
    severity = Column(Enum("critical", "high", "medium", "low"))
    title = Column(String, nullable=False)
    description = Column(Text)
    status = Column(Enum("new", "acknowledged", "resolved", "false-positive"))
    
    # Attack classification
    attack_type = Column(String)  # e.g., "T0846"
    attack_name = Column(String)  # e.g., "Port Scan"
    
    # Correlation
    correlation_confidence = Column(Float)
    correlation_summary = Column(String)
    
    # Context analysis (JSONB)
    context_analysis = Column(JSONB)
    
    # Relationships
    sources = relationship("AlertSource", back_populates="alert")
```

### AlertSource Model

```python
class AlertSource(Base):
    __tablename__ = "alert_sources"
    
    id = Column(UUID, primary_key=True)
    alert_id = Column(UUID, ForeignKey("alerts.id"))
    
    layer = Column(Integer)  # 1, 2, or 3
    model_name = Column(String)  # "LSTM", "Isolation Forest", etc.
    confidence = Column(Float)
    detection_time = Column(DateTime)
    evidence = Column(Text)
    context_evidence = Column(JSONB)
    
    # Relationship
    alert = relationship("Alert", back_populates="sources")
```

### FLRound Model

```python
class FLRound(Base):
    __tablename__ = "fl_rounds"
    
    id = Column(Integer, primary_key=True)
    round_number = Column(Integer, unique=True)
    status = Column(Enum("in-progress", "completed", "failed"))
    phase = Column(Enum("distributing", "training", "aggregating", "complete"))
    
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    progress = Column(Integer)  # 0-100
    epsilon = Column(Float)
    model_accuracy = Column(Float)
    
    clients_active = Column(Integer)
    total_clients = Column(Integer)
    
    # Relationships
    clients = relationship("FLClient", back_populates="round")
```

### FLClient Model

```python
class FLClient(Base):
    __tablename__ = "fl_clients"
    
    id = Column(UUID, primary_key=True)
    round_id = Column(Integer, ForeignKey("fl_rounds.id"))
    
    facility_id = Column(String)
    name = Column(String)
    status = Column(Enum("active", "delayed", "offline"))
    
    progress = Column(Integer)  # 0-100
    current_epoch = Column(Integer)
    total_epochs = Column(Integer)
    
    loss = Column(Float)
    accuracy = Column(Float)
    
    last_update = Column(DateTime)
    
    # Relationship
    round = relationship("FLRound", back_populates="clients")
```

### Prediction Model

```python
class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(UUID, primary_key=True)
    timestamp = Column(DateTime)
    
    current_technique = Column(String)
    current_technique_name = Column(String)
    alert_id = Column(UUID, ForeignKey("alerts.id"))
    
    validated = Column(Boolean, default=False)
    validation_time = Column(DateTime)
    
    # Relationships
    predicted_techniques = relationship("PredictedTechnique", back_populates="prediction")
```

### PredictedTechnique Model

```python
class PredictedTechnique(Base):
    __tablename__ = "predicted_techniques"
    
    id = Column(UUID, primary_key=True)
    prediction_id = Column(UUID, ForeignKey("predictions.id"))
    
    technique_id = Column(String)  # e.g., "T0800"
    technique_name = Column(String)
    probability = Column(Float)
    rank = Column(Integer)
    timeframe = Column(String)  # e.g., "15-60 minutes"
    
    # Relationship
    prediction = relationship("Prediction", back_populates="predicted_techniques")
```

### NetworkData Model

```python
class NetworkData(Base):
    __tablename__ = "network_data"
    
    id = Column(UUID, primary_key=True)
    timestamp = Column(DateTime, index=True)
    facility_id = Column(String, index=True)
    
    # Aggregated metrics
    packets_per_sec = Column(Integer)
    bytes_per_sec = Column(Integer)
    unique_src_ips = Column(Integer)
    unique_dest_ips = Column(Integer)
    protocol_distribution = Column(Float)
    failed_connections = Column(Integer)
    avg_packet_size = Column(Integer)
    inter_arrival_time = Column(Integer)
    
    # Raw features (JSONB for flexibility)
    raw_features = Column(JSONB)
```

---


## Pydantic Schemas

### Alert Schemas

```python
class AlertSourceSchema(BaseModel):
    layer: int
    model_name: str
    confidence: float
    detection_time: datetime
    evidence: str
    context_evidence: Optional[Dict] = None

class ContextAnalysis(BaseModel):
    duration: str
    pattern: str
    behavior: str
    timeline: List[Dict]
    evidence: Dict[str, str]

class AlertBase(BaseModel):
    facility_id: str
    severity: Literal["critical", "high", "medium", "low"]
    title: str
    description: str

class AlertCreate(AlertBase):
    sources: List[AlertSourceSchema]
    attack_type: Optional[str] = None
    attack_name: Optional[str] = None
    context_analysis: Optional[ContextAnalysis] = None

class AlertResponse(AlertBase):
    id: UUID
    timestamp: datetime
    status: Literal["new", "acknowledged", "resolved", "false-positive"]
    sources: List[AlertSourceSchema]
    correlation_confidence: Optional[float]
    correlation_summary: Optional[str]
    attack_type: Optional[str]
    attack_name: Optional[str]
    context_analysis: Optional[ContextAnalysis]
    
    class Config:
        from_attributes = True

class AlertUpdate(BaseModel):
    status: Literal["acknowledged", "resolved", "false-positive"]

class AlertStats(BaseModel):
    total: int
    critical: int
    unresolved: int
    false_positives: int
```

### FL Schemas

```python
class FLClientSchema(BaseModel):
    id: UUID
    facility_id: str
    name: str
    status: Literal["active", "delayed", "offline"]
    progress: int
    current_epoch: int
    total_epochs: int
    loss: float
    accuracy: float
    last_update: datetime
    
    class Config:
        from_attributes = True

class FLRoundBase(BaseModel):
    round_number: int
    status: Literal["in-progress", "completed", "failed"]
    phase: Literal["distributing", "training", "aggregating", "complete"]

class FLRoundResponse(FLRoundBase):
    id: int
    start_time: datetime
    end_time: Optional[datetime]
    progress: int
    epsilon: float
    model_accuracy: float
    clients_active: int
    total_clients: int
    clients: List[FLClientSchema]
    
    class Config:
        from_attributes = True

class PrivacyMetrics(BaseModel):
    epsilon: float
    delta: str
    data_size: str
    encryption: str
    privacy_budget_remaining: float
```

### Prediction Schemas

```python
class PredictedTechniqueSchema(BaseModel):
    technique_id: str
    technique_name: str
    probability: float
    rank: int
    timeframe: str

class PredictionBase(BaseModel):
    current_technique: str
    current_technique_name: str
    alert_id: UUID

class PredictionCreate(PredictionBase):
    predicted_techniques: List[PredictedTechniqueSchema]

class PredictionResponse(PredictionBase):
    id: UUID
    timestamp: datetime
    validated: bool
    validation_time: Optional[datetime]
    predicted_techniques: List[PredictedTechniqueSchema]
    
    class Config:
        from_attributes = True

class AttackGraphNode(BaseModel):
    id: str
    name: str
    type: Literal["current", "predicted"]
    probability: float

class AttackGraphLink(BaseModel):
    source: str
    target: str
    probability: float

class AttackGraphData(BaseModel):
    nodes: List[AttackGraphNode]
    links: List[AttackGraphLink]

class TechniqueDetails(BaseModel):
    id: str
    name: str
    description: str
    tactics: str
    detection: str
    mitigation: str
    platforms: str
    affected_assets: Optional[List[str]] = None
```

### Context Schemas

```python
class TimelinePoint(BaseModel):
    time: str
    packets_per_sec: int
    unique_dest_ips: int
    protocol_distribution: float
    status: Literal["normal", "suspicious", "attack"]

class ContextEvidence(BaseModel):
    packets_per_sec: str
    unique_dest_ips: str
    protocol_distribution: str
    failed_connections: str

class PatternAnalysis(BaseModel):
    pattern_type: str
    confidence: float
    description: str

class ContextEvidenceResponse(BaseModel):
    alert_id: UUID
    timeline: List[TimelinePoint]
    evidence: ContextEvidence
    pattern_analysis: PatternAnalysis
```

---


## Service Layer Architecture

### WebSocket Manager

```python
class WebSocketManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {
            "alerts": [],
            "fl_status": [],
            "predictions": [],
            "system": []
        }
    
    async def connect(self, websocket: WebSocket, channel: str):
        """Add new WebSocket connection to channel"""
        
    async def disconnect(self, websocket: WebSocket, channel: str):
        """Remove WebSocket connection from channel"""
        
    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connections in channel"""
        
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific connection"""
```

### Kafka Consumer Service

```python
class KafkaConsumerService:
    """Bridges Kafka topics to WebSocket channels"""
    
    def __init__(self, websocket_manager: WebSocketManager):
        self.ws_manager = websocket_manager
        self.consumer = AIOKafkaConsumer(...)
    
    async def start(self):
        """Start consuming from Kafka topics"""
        
    async def consume_alerts(self):
        """Consume alerts topic and broadcast to WebSocket"""
        async for message in self.consumer:
            alert_data = json.loads(message.value)
            await self.ws_manager.broadcast("alerts", {
                "channel": "alerts",
                "type": "new_alert",
                "data": alert_data
            })
    
    async def consume_fl_events(self):
        """Consume FL events and broadcast to WebSocket"""
        
    async def consume_predictions(self):
        """Consume predictions and broadcast to WebSocket"""
```

### Context Buffer Service

```python
class ContextBufferService:
    """Manages Redis context buffer operations"""
    
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
    
    async def store_packet_features(
        self, 
        facility_id: str, 
        features: Dict
    ):
        """Store packet features in 60-second rolling window"""
        key = f"context:{facility_id}"
        # Store with 60-second TTL
        await self.redis.zadd(
            key, 
            {json.dumps(features): time.time()}
        )
        # Remove entries older than 60 seconds
        cutoff = time.time() - 60
        await self.redis.zremrangebyscore(key, 0, cutoff)
    
    async def get_context_window(
        self, 
        facility_id: str
    ) -> List[Dict]:
        """Retrieve 60-second context window"""
        key = f"context:{facility_id}"
        entries = await self.redis.zrange(key, 0, -1)
        return [json.loads(e) for e in entries]
    
    async def get_context_for_alert(
        self, 
        alert_id: UUID
    ) -> Dict:
        """Retrieve stored context analysis for alert"""
        # Query from PostgreSQL alert.context_analysis
```

### Alert Service

```python
class AlertService:
    """Business logic for alert management"""
    
    def __init__(
        self, 
        alert_repo: AlertRepository,
        ws_manager: WebSocketManager
    ):
        self.alert_repo = alert_repo
        self.ws_manager = ws_manager
    
    async def create_alert(
        self, 
        alert_data: AlertCreate
    ) -> AlertResponse:
        """Create new alert and broadcast to WebSocket"""
        alert = await self.alert_repo.create(alert_data)
        
        # Broadcast to WebSocket
        await self.ws_manager.broadcast("alerts", {
            "channel": "alerts",
            "type": "new_alert",
            "data": alert.dict()
        })
        
        return alert
    
    async def update_alert_status(
        self, 
        alert_id: UUID, 
        status: str
    ) -> AlertResponse:
        """Update alert status and broadcast"""
        alert = await self.alert_repo.update_status(alert_id, status)
        
        await self.ws_manager.broadcast("alerts", {
            "channel": "alerts",
            "type": "alert_updated",
            "data": alert.dict()
        })
        
        return alert
    
    async def get_alerts(
        self, 
        filters: Dict
    ) -> Tuple[List[AlertResponse], int]:
        """Get filtered alerts with pagination"""
        return await self.alert_repo.get_all(filters)
    
    async def get_alert_stats(self) -> AlertStats:
        """Calculate alert statistics"""
        return await self.alert_repo.get_stats()
```

### FL Service

```python
class FLService:
    """Federated Learning service"""
    
    def __init__(
        self,
        fl_repo: FLRepository,
        ws_manager: WebSocketManager,
        fl_server_url: str
    ):
        self.fl_repo = fl_repo
        self.ws_manager = ws_manager
        self.fl_server_url = fl_server_url
    
    async def trigger_round(self) -> FLRoundResponse:
        """Trigger new FL round"""
        # Create round in database
        round_data = await self.fl_repo.create_round()
        
        # Call FL server to start round
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.fl_server_url}/start_round",
                json={"round_id": round_data.id}
            )
        
        # Broadcast to WebSocket
        await self.ws_manager.broadcast("fl_status", {
            "channel": "fl_status",
            "type": "round_started",
            "data": round_data.dict()
        })
        
        return round_data
    
    async def update_round_progress(
        self, 
        round_id: int, 
        progress: int
    ):
        """Update round progress and broadcast"""
        round_data = await self.fl_repo.update_progress(round_id, progress)
        
        await self.ws_manager.broadcast("fl_status", {
            "channel": "fl_status",
            "type": "progress_update",
            "data": round_data.dict()
        })
    
    async def get_current_round(self) -> Optional[FLRoundResponse]:
        """Get current active round"""
        return await self.fl_repo.get_current_round()
    
    async def get_clients(self) -> List[FLClientSchema]:
        """Get all FL clients"""
        return await self.fl_repo.get_all_clients()
```

### Prediction Service

```python
class PredictionService:
    """Attack prediction service"""
    
    def __init__(
        self,
        prediction_repo: PredictionRepository,
        neo4j_client: Neo4jClient,
        ws_manager: WebSocketManager
    ):
        self.prediction_repo = prediction_repo
        self.neo4j = neo4j_client
        self.ws_manager = ws_manager
    
    async def create_prediction(
        self, 
        current_technique: str,
        alert_id: UUID
    ) -> PredictionResponse:
        """Generate prediction using GNN"""
        # Query Neo4j for MITRE relationships
        next_techniques = await self.neo4j.get_next_techniques(
            current_technique
        )
        
        # Create prediction
        prediction = await self.prediction_repo.create({
            "current_technique": current_technique,
            "alert_id": alert_id,
            "predicted_techniques": next_techniques
        })
        
        # Broadcast to WebSocket
        await self.ws_manager.broadcast("predictions", {
            "channel": "predictions",
            "type": "new_prediction",
            "data": prediction.dict()
        })
        
        return prediction
    
    async def get_attack_graph(self) -> AttackGraphData:
        """Get MITRE ATT&CK graph from Neo4j"""
        return await self.neo4j.get_attack_graph()
    
    async def get_technique_details(
        self, 
        technique_id: str
    ) -> TechniqueDetails:
        """Get technique details from Neo4j"""
        return await self.neo4j.get_technique(technique_id)
```

---


## Repository Layer (Data Access)

### Alert Repository

```python
class AlertRepository:
    """Data access for alerts"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, alert_data: AlertCreate) -> Alert:
        """Create new alert with sources"""
        
    async def get_by_id(self, alert_id: UUID) -> Optional[Alert]:
        """Get alert by ID with sources"""
        
    async def get_all(
        self, 
        filters: Dict
    ) -> Tuple[List[Alert], int]:
        """Get filtered alerts with pagination"""
        
    async def update_status(
        self, 
        alert_id: UUID, 
        status: str
    ) -> Alert:
        """Update alert status"""
        
    async def get_stats(self) -> Dict:
        """Calculate alert statistics"""
```

### FL Repository

```python
class FLRepository:
    """Data access for FL rounds and clients"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_round(self) -> FLRound:
        """Create new FL round"""
        
    async def get_current_round(self) -> Optional[FLRound]:
        """Get current active round"""
        
    async def update_progress(
        self, 
        round_id: int, 
        progress: int
    ) -> FLRound:
        """Update round progress"""
        
    async def get_all_clients(self) -> List[FLClient]:
        """Get all FL clients"""
        
    async def update_client_status(
        self, 
        client_id: UUID, 
        status_data: Dict
    ) -> FLClient:
        """Update client status"""
```

### Prediction Repository

```python
class PredictionRepository:
    """Data access for predictions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, prediction_data: Dict) -> Prediction:
        """Create new prediction"""
        
    async def get_by_id(self, prediction_id: UUID) -> Optional[Prediction]:
        """Get prediction by ID"""
        
    async def get_all(self, filters: Dict) -> List[Prediction]:
        """Get filtered predictions"""
        
    async def validate_prediction(
        self, 
        prediction_id: UUID
    ) -> Prediction:
        """Mark prediction as validated"""
```

---

## FastAPI Dependencies

```python
# app/utils/dependencies.py

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with async_session_maker() as session:
        yield session

async def get_redis() -> Redis:
    """Redis client dependency"""
    return redis_client

async def get_neo4j() -> Neo4jClient:
    """Neo4j client dependency"""
    return neo4j_client

async def get_websocket_manager() -> WebSocketManager:
    """WebSocket manager dependency"""
    return websocket_manager

# Service dependencies
async def get_alert_service(
    db: AsyncSession = Depends(get_db),
    ws_manager: WebSocketManager = Depends(get_websocket_manager)
) -> AlertService:
    """Alert service dependency"""
    alert_repo = AlertRepository(db)
    return AlertService(alert_repo, ws_manager)

async def get_fl_service(
    db: AsyncSession = Depends(get_db),
    ws_manager: WebSocketManager = Depends(get_websocket_manager)
) -> FLService:
    """FL service dependency"""
    fl_repo = FLRepository(db)
    return FLService(fl_repo, ws_manager, settings.FL_SERVER_URL)

async def get_prediction_service(
    db: AsyncSession = Depends(get_db),
    neo4j: Neo4jClient = Depends(get_neo4j),
    ws_manager: WebSocketManager = Depends(get_websocket_manager)
) -> PredictionService:
    """Prediction service dependency"""
    prediction_repo = PredictionRepository(db)
    return PredictionService(prediction_repo, neo4j, ws_manager)
```

---

## Main Application Setup

```python
# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api import alerts, fl_status, predictions, context, demo, websocket
from app.services.kafka_consumer import KafkaConsumerService
from app.services.websocket_manager import WebSocketManager

# Initialize WebSocket manager
websocket_manager = WebSocketManager()

# Initialize Kafka consumer
kafka_consumer = KafkaConsumerService(websocket_manager)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await kafka_consumer.start()
    yield
    # Shutdown
    await kafka_consumer.stop()

app = FastAPI(
    title="ICS Threat Detection API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
app.include_router(fl_status.router, prefix="/api/fl", tags=["fl"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["predictions"])
app.include_router(context.router, prefix="/api/context", tags=["context"])
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "redis": "connected",
            "kafka": "connected",
            "neo4j": "connected"
        }
    }

@app.get("/api/system/status")
async def system_status():
    """System status endpoint"""
    # Get real-time system metrics
    return {
        "active_alerts": 12,
        "fl_progress": 67,
        "prediction_accuracy": 89
    }
```

---


## Configuration Management

```python
# app/config.py

from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    
    # Redis (Context Buffer)
    REDIS_URL: str
    REDIS_MAX_CONNECTIONS: int = 10
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str
    KAFKA_GROUP_ID: str = "ics_threat_detection"
    KAFKA_AUTO_OFFSET_RESET: str = "earliest"
    
    # Neo4j
    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    
    # FL Server
    FL_SERVER_URL: str = "http://localhost:8080"
    FL_MIN_CLIENTS: int = 3
    
    # Demo Mode
    DEMO_MODE: bool = True
    SEED_DATA_ON_STARTUP: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## Database Connection

```python
# app/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    future=True
)

# Create session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Redis connection
import redis.asyncio as redis

redis_client = redis.from_url(
    settings.REDIS_URL,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    decode_responses=True
)

# Neo4j connection
from neo4j import AsyncGraphDatabase

class Neo4jClient:
    def __init__(self):
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
    
    async def close(self):
        await self.driver.close()
    
    async def get_attack_graph(self) -> Dict:
        """Query MITRE ATT&CK graph"""
        async with self.driver.session() as session:
            result = await session.run("""
                MATCH (t:Technique)-[r:LEADS_TO]->(next:Technique)
                RETURN t, r, next
            """)
            # Process and return graph data
    
    async def get_next_techniques(self, current_technique: str) -> List[Dict]:
        """Get predicted next techniques"""
        async with self.driver.session() as session:
            result = await session.run("""
                MATCH (t:Technique {id: $technique_id})-[r:LEADS_TO]->(next:Technique)
                RETURN next, r.probability as probability
                ORDER BY probability DESC
                LIMIT 3
            """, technique_id=current_technique)
            # Process and return predictions

neo4j_client = Neo4jClient()
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Goal**: Basic API with mock data

**Tasks**:
1. ✅ Set up FastAPI project structure
2. ✅ Configure PostgreSQL connection
3. ✅ Create SQLAlchemy models
4. ✅ Create Pydantic schemas
5. ✅ Implement basic CRUD endpoints
6. ✅ Load seed data from webapp mock data
7. ✅ Test with Postman/curl

**Deliverables**:
- Working API with health check
- Alerts endpoints returning data
- FL status endpoints returning data
- Predictions endpoints returning data

### Phase 2: WebSocket Integration (Week 1-2)
**Goal**: Real-time communication

**Tasks**:
1. ✅ Implement WebSocket manager
2. ✅ Set up Kafka consumer service
3. ✅ Bridge Kafka to WebSocket
4. ✅ Test real-time message flow
5. ✅ Update webapp to connect to WebSocket

**Deliverables**:
- WebSocket endpoint working
- Real-time alerts appearing in webapp
- FL progress updates in real-time

### Phase 3: Context Buffer (Week 2)
**Goal**: Context analysis API

**Tasks**:
1. ✅ Set up Redis connection
2. ✅ Implement context buffer service
3. ✅ Create context API endpoints
4. ✅ Add context analysis to alerts
5. ✅ Update webapp to display context

**Deliverables**:
- Context buffer storing 60-second windows
- Context evidence API working
- Timeline visualization in webapp

### Phase 4: Detection Integration (Week 2-3)
**Goal**: Connect detection models

**Tasks**:
1. ✅ Create detection service wrappers
2. ✅ Integrate LSTM Autoencoder
3. ✅ Integrate Isolation Forest
4. ✅ Integrate Threat Classifier
5. ✅ Test end-to-end detection flow

**Deliverables**:
- Real alerts from detection models
- Multi-source correlation working
- Attack classification displayed

### Phase 5: FL Integration (Week 3)
**Goal**: Federated learning working

**Tasks**:
1. ✅ Set up Flower FL server
2. ✅ Create FL service wrapper
3. ✅ Implement FL round triggering
4. ✅ Add FL event streaming
5. ✅ Test complete FL round

**Deliverables**:
- FL rounds can be triggered from webapp
- Live progress updates working
- Client status displayed correctly

### Phase 6: Attack Prediction (Week 3)
**Goal**: GNN predictions working

**Tasks**:
1. ✅ Load MITRE ATT&CK into Neo4j
2. ✅ Implement Neo4j queries
3. ✅ Create prediction service
4. ✅ Integrate GNN model
5. ✅ Test prediction flow

**Deliverables**:
- Attack graph displaying correctly
- Predictions generated for attacks
- Technique details showing

### Phase 7: Demo Scenarios (Week 4)
**Goal**: Demo orchestration

**Tasks**:
1. ✅ Implement demo API endpoints
2. ✅ Create scenario orchestration
3. ✅ Test all demo scenarios
4. ✅ Add demo controls to webapp
5. ✅ Verify reliability (10x runs)

**Deliverables**:
- Port scan demo working
- FL round demo working
- Multi-stage attack demo working
- All scenarios reliable

---

## Testing Strategy

### Unit Tests
```python
# tests/test_services/test_alert_service.py

@pytest.mark.asyncio
async def test_create_alert():
    """Test alert creation"""
    alert_data = AlertCreate(...)
    alert = await alert_service.create_alert(alert_data)
    assert alert.id is not None
    assert alert.status == "new"
```

### Integration Tests
```python
# tests/test_api/test_alerts.py

@pytest.mark.asyncio
async def test_get_alerts_endpoint(client):
    """Test GET /api/alerts endpoint"""
    response = await client.get("/api/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()
```

### End-to-End Tests
```python
# tests/test_e2e/test_detection_flow.py

@pytest.mark.asyncio
async def test_detection_to_webapp_flow():
    """Test complete flow from detection to webapp"""
    # 1. Simulate network traffic
    # 2. Verify detection
    # 3. Check alert in database
    # 4. Verify WebSocket broadcast
    # 5. Confirm webapp receives update
```

---

## Monitoring & Logging

### Logging Configuration
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Metrics to Track
- API response times (p50, p95, p99)
- WebSocket connection count
- Kafka consumer lag
- Database query performance
- Redis hit/miss ratio
- Alert creation rate
- FL round duration

---

## Security Considerations

1. **API Authentication** (Future)
   - JWT tokens for API access
   - Role-based access control

2. **Input Validation**
   - Pydantic schemas validate all inputs
   - SQL injection prevention (SQLAlchemy ORM)

3. **CORS Configuration**
   - Restrict to known origins
   - Credentials handling

4. **Rate Limiting** (Future)
   - Prevent API abuse
   - WebSocket connection limits

5. **Data Privacy**
   - Context buffer auto-expires (60 seconds)
   - Differential privacy in FL
   - No raw packet storage

---

## Performance Optimization

1. **Database**
   - Index on timestamp, facility_id
   - Connection pooling
   - Query optimization

2. **Redis**
   - Connection pooling
   - Efficient data structures
   - TTL for automatic cleanup

3. **WebSocket**
   - Connection pooling
   - Message batching
   - Compression

4. **API**
   - Async/await throughout
   - Response caching (future)
   - Pagination for large datasets

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** Architecture Specification  
**Based On:** Idea_and_architecture folder specifications
