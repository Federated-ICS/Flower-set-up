# Backend Architecture

## System Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        WebApp[React WebApp<br/>Port 3000]
    end

    subgraph "API Gateway Layer"
        FastAPI[FastAPI Server<br/>Port 8000]
        WS[WebSocket Manager]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Alerts, FL Rounds)]
        Redis[(Redis<br/>Context Buffer)]
        Neo4j[(Neo4j<br/>MITRE ATT&CK)]
    end

    subgraph "Message Bus"
        Kafka[Apache Kafka<br/>Event Streaming]
    end

    subgraph "Detection Services"
        LSTM[LSTM Autoencoder<br/>Layer 1]
        IF[Isolation Forest<br/>Layer 1]
        Classifier[Threat Classifier<br/>Layer 2]
        GNN[Graph Neural Network<br/>Layer 3]
    end

    subgraph "Federated Learning"
        FLServer[FL Server<br/>Flower]
        FLClient1[FL Client A]
        FLClient2[FL Client B]
        FLClient3[FL Client C]
    end

    subgraph "Simulation"
        Simulator[Network Traffic<br/>Simulator]
    end

    WebApp <-->|REST + WebSocket| FastAPI
    FastAPI <--> WS
    FastAPI <--> PG
    FastAPI <--> Redis
    FastAPI <--> Neo4j
    
    WS <-->|Subscribe| Kafka
    
    Simulator -->|Publish| Kafka
    Kafka -->|Consume| LSTM
    Kafka -->|Consume| IF
    
    LSTM -->|Anomaly| Kafka
    IF -->|Anomaly| Kafka
    
    Kafka -->|Trigger| Classifier
    Classifier -->|Attack Type| Kafka
    
    Kafka -->|Trigger| GNN
    GNN <-->|Query Graph| Neo4j
    GNN -->|Prediction| Kafka
    
    Kafka -->|Store| PG
    LSTM <-->|Context| Redis
    Classifier <-->|Context| Redis
    
    FastAPI <-->|gRPC/REST| FLServer
    FLServer <--> FLClient1
    FLServer <--> FLClient2
    FLServer <--> FLClient3
    
    FLClient1 -->|Events| Kafka
    FLClient2 -->|Events| Kafka
    FLClient3 -->|Events| Kafka

    style FastAPI fill:#3b82f6
    style WebApp fill:#10b981
    style Kafka fill:#f59e0b
    style PG fill:#8b5cf6
    style Redis fill:#ef4444
    style Neo4j fill:#06b6d4
```

## Detailed Component Architecture

```mermaid
graph TB
    subgraph "FastAPI Application Structure"
        Main[main.py<br/>Application Entry]
        
        subgraph "API Routes"
            AlertsAPI[/api/alerts]
            FLAPI[/api/fl]
            PredAPI[/api/predictions]
            DemoAPI[/api/demo]
            HealthAPI[/health]
        end
        
        subgraph "Services"
            KafkaConsumer[Kafka Consumer<br/>Bridge]
            WSManager[WebSocket Manager<br/>Pub/Sub]
            ContextBuffer[Context Buffer<br/>Service]
            FLService[FL Service<br/>Wrapper]
        end
        
        subgraph "Data Access"
            AlertsDB[Alerts Repository]
            FLDB[FL Rounds Repository]
            PredDB[Predictions Repository]
            GraphDB[Graph Repository]
        end
        
        subgraph "Models & Schemas"
            SQLModels[SQLAlchemy Models]
            Pydantic[Pydantic Schemas]
        end
        
        Main --> AlertsAPI
        Main --> FLAPI
        Main --> PredAPI
        Main --> DemoAPI
        Main --> HealthAPI
        
        AlertsAPI --> AlertsDB
        FLAPI --> FLDB
        PredAPI --> PredDB
        PredAPI --> GraphDB
        
        AlertsAPI --> WSManager
        FLAPI --> WSManager
        PredAPI --> WSManager
        
        KafkaConsumer --> WSManager
        KafkaConsumer --> AlertsDB
        
        AlertsDB --> SQLModels
        FLDB --> SQLModels
        PredDB --> SQLModels
        
        AlertsAPI --> Pydantic
        FLAPI --> Pydantic
        PredAPI --> Pydantic
        
        ContextBuffer --> Redis[(Redis)]
        AlertsDB --> PG[(PostgreSQL)]
        GraphDB --> Neo4j[(Neo4j)]
    end

    style Main fill:#3b82f6
    style KafkaConsumer fill:#f59e0b
    style WSManager fill:#10b981
```

## Data Flow Diagrams

### Alert Detection Flow

```mermaid
sequenceDiagram
    participant Sim as Network Simulator
    participant K as Kafka
    participant LSTM as LSTM Autoencoder
    participant IF as Isolation Forest
    participant Cls as Threat Classifier
    participant DB as PostgreSQL
    participant API as FastAPI
    participant WS as WebSocket
    participant Web as WebApp

    Sim->>K: Publish network_data
    K->>LSTM: Consume packet features
    K->>IF: Consume packet features
    
    LSTM->>LSTM: Analyze 60s context
    IF->>IF: Analyze single packet
    
    alt Anomaly Detected
        LSTM->>K: Publish anomaly alert
        IF->>K: Publish anomaly alert
        
        K->>Cls: Trigger classification
        Cls->>Cls: Analyze context patterns
        Cls->>K: Publish attack type
        
        K->>DB: Store alert
        K->>API: Forward to consumer
        API->>WS: Broadcast alert
        WS->>Web: Real-time update
    end
```

### Federated Learning Round Flow

```mermaid
sequenceDiagram
    participant Web as WebApp
    participant API as FastAPI
    participant FLS as FL Server
    participant FC1 as FL Client A
    participant FC2 as FL Client B
    participant FC3 as FL Client C
    participant K as Kafka
    participant DB as PostgreSQL
    participant WS as WebSocket

    Web->>API: POST /api/fl/rounds/trigger
    API->>FLS: Start FL Round
    API->>DB: Create round record
    
    FLS->>FC1: Distribute global model
    FLS->>FC2: Distribute global model
    FLS->>FC3: Distribute global model
    
    par Local Training
        FC1->>FC1: Train on local data
        FC2->>FC2: Train on local data
        FC3->>FC3: Train on local data
    end
    
    FC1->>K: Publish training progress
    FC2->>K: Publish training progress
    FC3->>K: Publish training progress
    
    K->>API: Forward progress events
    API->>WS: Broadcast progress
    WS->>Web: Update UI
    
    FC1->>FLS: Upload model weights
    FC2->>FLS: Upload model weights
    FC3->>FLS: Upload model weights
    
    FLS->>FLS: Aggregate weights
    FLS->>K: Publish aggregation complete
    
    FLS->>FC1: Distribute updated model
    FLS->>FC2: Distribute updated model
    FLS->>FC3: Distribute updated model
    
    FLS->>API: Round complete
    API->>DB: Update round status
    API->>WS: Broadcast completion
    WS->>Web: Update UI
```

### Attack Prediction Flow

```mermaid
sequenceDiagram
    participant K as Kafka
    participant API as FastAPI
    participant GNN as GNN Service
    participant Neo4j as Neo4j
    participant DB as PostgreSQL
    participant WS as WebSocket
    participant Web as WebApp

    K->>API: Attack classified (T0846)
    API->>GNN: Request prediction
    
    GNN->>Neo4j: Query MITRE graph
    Neo4j-->>GNN: Return relationships
    
    GNN->>GNN: Calculate probabilities
    GNN-->>API: Top-3 predictions
    
    API->>DB: Store prediction
    API->>WS: Broadcast prediction
    WS->>Web: Update attack graph
    
    Note over Web: Display predicted<br/>techniques with<br/>probabilities
```

## Database Schema

```mermaid
erDiagram
    ALERTS ||--o{ ALERT_SOURCES : has
    ALERTS {
        uuid id PK
        timestamp created_at
        string facility_id
        string severity
        string title
        text description
        string status
        float confidence
        jsonb metadata
    }
    
    ALERT_SOURCES {
        uuid id PK
        uuid alert_id FK
        int layer
        string model_name
        float confidence
        jsonb context_evidence
    }
    
    FL_ROUNDS ||--o{ FL_CLIENTS : includes
    FL_ROUNDS {
        int id PK
        timestamp start_time
        timestamp end_time
        int round_number
        string phase
        int progress
        float epsilon
        float model_accuracy
        string status
    }
    
    FL_CLIENTS {
        uuid id PK
        int round_id FK
        string facility_id
        string status
        int progress
        float loss
        float accuracy
        timestamp last_update
    }
    
    PREDICTIONS ||--o{ PREDICTED_TECHNIQUES : contains
    PREDICTIONS {
        uuid id PK
        timestamp created_at
        string current_technique
        uuid alert_id FK
        boolean validated
    }
    
    PREDICTED_TECHNIQUES {
        uuid id PK
        uuid prediction_id FK
        string technique_id
        string technique_name
        float probability
        int rank
    }
    
    NETWORK_DATA {
        uuid id PK
        timestamp created_at
        string facility_id
        int packets_per_sec
        int bytes_per_sec
        int unique_src_ips
        int unique_dest_ips
        float protocol_distribution
        int failed_connections
        jsonb raw_features
    }
```

## WebSocket Architecture

```mermaid
graph TB
    subgraph "WebSocket Manager"
        WSManager[WebSocket Manager]
        
        subgraph "Channels"
            AlertsChan[alerts channel]
            FLChan[fl_status channel]
            PredChan[predictions channel]
            SysChan[system channel]
        end
        
        subgraph "Connection Pool"
            Conn1[Connection 1]
            Conn2[Connection 2]
            Conn3[Connection N]
        end
    end
    
    subgraph "Event Sources"
        KafkaConsumer[Kafka Consumer]
        APIEndpoints[API Endpoints]
        Services[Background Services]
    end
    
    subgraph "Clients"
        WebApp1[WebApp Instance 1]
        WebApp2[WebApp Instance 2]
    end
    
    KafkaConsumer -->|Publish| AlertsChan
    KafkaConsumer -->|Publish| FLChan
    KafkaConsumer -->|Publish| PredChan
    
    APIEndpoints -->|Publish| AlertsChan
    APIEndpoints -->|Publish| FLChan
    
    Services -->|Publish| SysChan
    
    AlertsChan --> WSManager
    FLChan --> WSManager
    PredChan --> WSManager
    SysChan --> WSManager
    
    WSManager --> Conn1
    WSManager --> Conn2
    WSManager --> Conn3
    
    Conn1 <--> WebApp1
    Conn2 <--> WebApp2
    Conn3 <--> WebApp2

    style WSManager fill:#3b82f6
    style KafkaConsumer fill:#f59e0b
```

## Context Buffer Architecture

```mermaid
graph LR
    subgraph "Context Buffer (Redis)"
        subgraph "Facility A Buffer"
            FA_Window[60-second<br/>Rolling Window]
            FA_Features[Packet Features<br/>~300KB]
        end
        
        subgraph "Facility B Buffer"
            FB_Window[60-second<br/>Rolling Window]
            FB_Features[Packet Features<br/>~300KB]
        end
        
        subgraph "Facility C Buffer"
            FC_Window[60-second<br/>Rolling Window]
            FC_Features[Packet Features<br/>~300KB]
        end
    end
    
    subgraph "Writers"
        Simulator[Network Simulator]
    end
    
    subgraph "Readers"
        LSTM[LSTM Autoencoder]
        Classifier[Threat Classifier]
    end
    
    Simulator -->|Write| FA_Window
    Simulator -->|Write| FB_Window
    Simulator -->|Write| FC_Window
    
    FA_Window -->|Read Sequences| LSTM
    FB_Window -->|Read Sequences| LSTM
    FC_Window -->|Read Sequences| LSTM
    
    FA_Window -->|Read Context| Classifier
    FB_Window -->|Read Context| Classifier
    FC_Window -->|Read Context| Classifier

    style FA_Window fill:#ef4444
    style FB_Window fill:#ef4444
    style FC_Window fill:#ef4444
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Docker Compose Stack"
        subgraph "Application Services"
            FastAPI[FastAPI Container<br/>Port 8000]
            KafkaConsumer[Kafka Consumer<br/>Container]
        end
        
        subgraph "Infrastructure Services"
            PostgreSQL[PostgreSQL<br/>Port 5432]
            Redis[Redis<br/>Port 6379]
            Neo4j[Neo4j<br/>Port 7474, 7687]
            Kafka[Kafka<br/>Port 9092]
            Zookeeper[Zookeeper<br/>Port 2181]
        end
        
        subgraph "Detection Services"
            DetectionService[Detection Service<br/>Container]
        end
        
        subgraph "FL Services"
            FLServer[FL Server<br/>Port 8080]
            FLClient1[FL Client A]
            FLClient2[FL Client B]
            FLClient3[FL Client C]
        end
    end
    
    subgraph "External"
        WebApp[React WebApp<br/>Port 3000]
    end
    
    WebApp <--> FastAPI
    FastAPI <--> PostgreSQL
    FastAPI <--> Redis
    FastAPI <--> Neo4j
    FastAPI <--> FLServer
    
    KafkaConsumer <--> Kafka
    KafkaConsumer <--> FastAPI
    
    DetectionService <--> Kafka
    DetectionService <--> Redis
    
    Kafka <--> Zookeeper
    
    FLServer <--> FLClient1
    FLServer <--> FLClient2
    FLServer <--> FLClient3
    
    FLClient1 <--> Kafka
    FLClient2 <--> Kafka
    FLClient3 <--> Kafka

    style FastAPI fill:#3b82f6
    style WebApp fill:#10b981
    style Kafka fill:#f59e0b
```

## API Layer Structure

```mermaid
graph TB
    subgraph "FastAPI Application"
        Main[main.py]
        
        subgraph "Routers"
            AlertsRouter[alerts.py<br/>/api/alerts]
            FLRouter[fl_status.py<br/>/api/fl]
            PredRouter[predictions.py<br/>/api/predictions]
            DemoRouter[demo.py<br/>/api/demo]
            WSRouter[websocket.py<br/>/ws]
        end
        
        subgraph "Dependencies"
            DBDep[get_db]
            RedisDep[get_redis]
            Neo4jDep[get_neo4j]
            AuthDep[verify_token]
        end
        
        subgraph "Middleware"
            CORS[CORS Middleware]
            Logging[Logging Middleware]
            ErrorHandler[Error Handler]
        end
        
        Main --> CORS
        Main --> Logging
        Main --> ErrorHandler
        
        Main --> AlertsRouter
        Main --> FLRouter
        Main --> PredRouter
        Main --> DemoRouter
        Main --> WSRouter
        
        AlertsRouter -.->|inject| DBDep
        FLRouter -.->|inject| DBDep
        PredRouter -.->|inject| DBDep
        PredRouter -.->|inject| Neo4jDep
        
        WSRouter -.->|inject| RedisDep
    end

    style Main fill:#3b82f6
    style AlertsRouter fill:#10b981
    style FLRouter fill:#f59e0b
    style PredRouter fill:#8b5cf6
```

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** Architecture Documentation
