# API Testing Guide

## 🚀 Quick Start

### 1. Start the Backend

```bash
# Make sure PostgreSQL is running
docker-compose up -d postgres

# Seed the database
poetry run python scripts/seed_database.py

# Start the API server (if not already running)
poetry run uvicorn app.main:app --reload --port 8000
```

### 2. Test the API

**Option A: Interactive Swagger UI**
```
http://localhost:8000/docs
```
- Click on any endpoint
- Click "Try it out"
- Fill in parameters
- Click "Execute"
- See the response!

**Option B: Command Line**
```bash
./scripts/test_api.sh
```

**Option C: Manual curl commands** (see below)

---

## 📊 Available Endpoints

### Health & System

```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/
```

### Alerts API

```bash
# Get all alerts (with pagination)
curl "http://localhost:8000/api/alerts?page=1&limit=10"

# Filter by severity
curl "http://localhost:8000/api/alerts?severity=critical"

# Filter by facility
curl "http://localhost:8000/api/alerts?facility=facility_a"

# Search alerts
curl "http://localhost:8000/api/alerts?search=Port"

# Get alert statistics
curl http://localhost:8000/api/alerts/stats

# Get specific alert (replace with actual ID)
curl http://localhost:8000/api/alerts/{alert-id}

# Update alert status
curl -X PUT http://localhost:8000/api/alerts/{alert-id}/status \
  -H "Content-Type: application/json" \
  -d '{"status": "acknowledged"}'

# Create new alert
curl -X POST http://localhost:8000/api/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "facility_id": "facility_a",
    "severity": "high",
    "title": "Test Alert",
    "description": "Test description",
    "sources": [
      {
        "layer": 1,
        "model_name": "LSTM Autoencoder",
        "confidence": 0.95,
        "detection_time": "2025-11-11T00:00:00",
        "evidence": "Anomaly detected"
      }
    ]
  }'
```

### Federated Learning API

```bash
# Get current FL round
curl http://localhost:8000/api/fl/rounds/current

# Get all FL rounds
curl http://localhost:8000/api/fl/rounds

# Get specific round
curl http://localhost:8000/api/fl/rounds/1

# Get all FL clients
curl http://localhost:8000/api/fl/clients

# Get specific client
curl http://localhost:8000/api/fl/clients/{client-id}

# Get privacy metrics
curl http://localhost:8000/api/fl/privacy-metrics

# Trigger new FL round
curl -X POST http://localhost:8000/api/fl/rounds/trigger

# Update round progress
curl -X PUT http://localhost:8000/api/fl/rounds/1/progress \
  -H "Content-Type: application/json" \
  -d '{"progress": 75, "phase": "training"}'

# Complete FL round
curl -X POST http://localhost:8000/api/fl/rounds/1/complete \
  -H "Content-Type: application/json" \
  -d '{"model_accuracy": 95.5}'

# Update client progress
curl -X PUT http://localhost:8000/api/fl/clients/{client-id} \
  -H "Content-Type: application/json" \
  -d '{
    "progress": 80,
    "current_epoch": 8,
    "loss": 0.12,
    "accuracy": 94.5
  }'
```

### Predictions API

```bash
# Get all predictions
curl http://localhost:8000/api/predictions

# Get latest prediction
curl http://localhost:8000/api/predictions/latest

# Get specific prediction
curl http://localhost:8000/api/predictions/{prediction-id}

# Filter by validation status
curl "http://localhost:8000/api/predictions?validated=true"

# Create new prediction
curl -X POST http://localhost:8000/api/predictions \
  -H "Content-Type: application/json" \
  -d '{
    "current_technique": "T0846",
    "current_technique_name": "Port Scan",
    "alert_id": "{alert-id}",
    "predicted_techniques": [
      {
        "technique_id": "T0800",
        "technique_name": "Lateral Movement",
        "probability": 0.72,
        "rank": 1,
        "timeframe": "15-60 minutes"
      }
    ]
  }'

# Validate prediction
curl -X POST http://localhost:8000/api/predictions/{prediction-id}/validate
```

---

## 🧪 Test Scenarios

### Scenario 1: View System Status

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Get alert statistics
curl http://localhost:8000/api/alerts/stats

# 3. Get current FL round
curl http://localhost:8000/api/fl/rounds/current

# 4. Get latest prediction
curl http://localhost:8000/api/predictions/latest
```

### Scenario 2: Alert Management

```bash
# 1. Get all critical alerts
curl "http://localhost:8000/api/alerts?severity=critical"

# 2. Get a specific alert (copy ID from previous response)
ALERT_ID="<paste-id-here>"
curl "http://localhost:8000/api/alerts/$ALERT_ID"

# 3. Acknowledge the alert
curl -X PUT "http://localhost:8000/api/alerts/$ALERT_ID/status" \
  -H "Content-Type: application/json" \
  -d '{"status": "acknowledged"}'

# 4. Verify the update
curl "http://localhost:8000/api/alerts/$ALERT_ID"
```

### Scenario 3: FL Round Workflow

```bash
# 1. Check current round
curl http://localhost:8000/api/fl/rounds/current

# 2. Get all clients
curl http://localhost:8000/api/fl/clients

# 3. Trigger new round
curl -X POST http://localhost:8000/api/fl/rounds/trigger

# 4. Check the new round
curl http://localhost:8000/api/fl/rounds/current
```

### Scenario 4: Attack Prediction

```bash
# 1. Get latest prediction
curl http://localhost:8000/api/predictions/latest

# 2. Get all predictions
curl http://localhost:8000/api/predictions

# 3. Validate a prediction (copy ID from response)
PRED_ID="<paste-id-here>"
curl -X POST "http://localhost:8000/api/predictions/$PRED_ID/validate"
```

---

## 📈 Sample Data

After running `seed_database.py`, you'll have:

- **20 Alerts** across 6 facilities
  - 7 critical alerts
  - Various attack types (Port Scan, Brute Force, DNS Tunneling, etc.)
  - Multiple detection sources (LSTM, Isolation Forest, Classifier)

- **4 FL Rounds**
  - 3 completed rounds (96%+ accuracy)
  - 1 in-progress round (training phase)
  - 6 clients per round (Facility A-F)

- **10 Predictions**
  - MITRE ATT&CK technique chains
  - Probabilities ranging from 55-78%
  - Some validated, some pending

---

## 🔍 Response Examples

### Alert Response
```json
{
  "id": "uuid",
  "timestamp": "2025-11-11T00:00:00",
  "facility_id": "facility_a",
  "severity": "critical",
  "title": "Port Scan Detected",
  "description": "Unusual port scanning activity",
  "status": "new",
  "attack_type": "T0846",
  "attack_name": "Port Scan",
  "sources": [
    {
      "layer": 1,
      "model_name": "LSTM Autoencoder",
      "confidence": 0.95,
      "evidence": "Anomaly score: 0.93"
    }
  ]
}
```

### FL Round Response
```json
{
  "id": 4,
  "round_number": 4,
  "status": "in-progress",
  "phase": "training",
  "progress": 67,
  "epsilon": 0.5,
  "model_accuracy": null,
  "clients": [
    {
      "id": "uuid",
      "facility_id": "facility_a",
      "name": "Facility A",
      "status": "active",
      "progress": 85,
      "current_epoch": 8,
      "loss": 0.12,
      "accuracy": 94.2
    }
  ]
}
```

### Prediction Response
```json
{
  "id": "uuid",
  "timestamp": "2025-11-11T00:00:00",
  "current_technique": "T0846",
  "current_technique_name": "Port Scan",
  "alert_id": "uuid",
  "validated": false,
  "predicted_techniques": [
    {
      "technique_id": "T0800",
      "technique_name": "Lateral Movement",
      "probability": 0.72,
      "rank": 1,
      "timeframe": "15-60 minutes"
    }
  ]
}
```

---

## 🛠️ Troubleshooting

### Server not responding
```bash
# Check if server is running
curl http://localhost:8000/health

# If not, start it
poetry run uvicorn app.main:app --reload --port 8000
```

### No data returned
```bash
# Reseed the database
poetry run python scripts/clear_database.py
poetry run python scripts/seed_database.py
```

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps

# Restart if needed
docker-compose restart postgres
```

### Port 8000 already in use
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>
```

---

## 📚 Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

---

**Last Updated**: November 11, 2025  
**API Version**: 1.0.0
