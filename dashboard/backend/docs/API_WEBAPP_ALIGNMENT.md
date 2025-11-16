# API-WebApp Alignment Document

This document maps the exact API requirements from the webapp to the backend implementation.

---

## WebApp Data Requirements Analysis

### 1. Dashboard Page (`/`)

**Current Mock Data Used:**
```typescript
// From webapp/app/page.tsx
const mockAlerts = [
  { id, title, severity, facility, timestamp }
]

const mockFacilities = [
  { name, status }
]

const systemStatus = {
  activeAlerts: 12,
  flProgress: 67,
  predictionAccuracy: 89
}

const flStatus = {
  roundNumber: 42,
  progress: 67,
  facilities: mockFacilities,
  epsilon: 0.5,
  delta: "10⁻⁵"
}

const attackPrediction = {
  techniqueId: "T1190",
  techniqueName: "Exploit Public-Facing Application",
  confidence: 76,
  timelineProgress: 65
}
```

**Backend API Endpoints Needed:**

```
GET /api/system/status
Response: {
  active_alerts: number,
  fl_progress: number,
  prediction_accuracy: number
}

GET /api/alerts?limit=3&status=new,acknowledged
Response: {
  alerts: Array<{
    id: string,
    title: string,
    severity: "critical" | "high" | "medium" | "low",
    facility: string,
    timestamp: string
  }>
}

GET /api/fl/rounds/current
Response: {
  round_number: number,
  progress: number,
  epsilon: number,
  delta: string,
  facilities: Array<{
    name: string,
    status: "active" | "delayed" | "offline"
  }>
}

GET /api/predictions/latest
Response: {
  technique_id: string,
  technique_name: string,
  confidence: number,
  timeline_progress: number
}
```

---

### 2. Alerts Page (`/alerts`)

**Current Mock Data Structure:**
```typescript
// From webapp/utils/mock-data.ts
interface Alert {
  id: string
  title: string
  description: string
  severity: "critical" | "high" | "medium" | "low"
  facility: string
  source: string  // "LSTM Model", "Isolation Forest", etc.
  timestamp: string
  status: "new" | "acknowledged" | "resolved" | "false-positive"
  relativeTime: string  // "2 min ago"
}

// 20 sample alerts in mockAlerts array
```

**WebApp Features:**
- Pagination (10 items per page)
- Filtering by: severity, facility, time range, status
- Search by: title, description
- Statistics: total, critical, unresolved, false_positives
- Actions: acknowledge, resolve, mark false-positive

**Backend API Endpoints Needed:**

```
GET /api/alerts
Query Parameters:
  - severity: "critical" | "high" | "medium" | "low" | "all"
  - facility: string | "All Facilities"
  - status: "new" | "acknowledged" | "resolved" | "false-positive"
  - search: string (searches title + description)
  - page: number (default: 1)
  - limit: number (default: 10)
  - time_range: "Last 24 hours" | "Last 7 days" | "Last 30 days"

Response: {
  alerts: Alert[],
  total: number,
  page: number,
  pages: number,
  limit: number
}

GET /api/alerts/{alert_id}
Response: Alert (full details with context)

PUT /api/alerts/{alert_id}/status
Body: {
  status: "acknowledged" | "resolved" | "false-positive"
}
Response: Alert (updated)

GET /api/alerts/stats
Response: {
  total: number,
  critical: number,
  unresolved: number,
  false_positives: number
}
```

**Alert Schema (Backend → WebApp):**
```typescript
{
  id: string,
  title: string,
  description: string,
  severity: "critical" | "high" | "medium" | "low",
  facility: string,
  source: string,  // Keep for backward compatibility
  timestamp: string,  // ISO 8601 format
  status: "new" | "acknowledged" | "resolved" | "false-positive",
  relative_time: string,  // Backend calculates "2 min ago"
  
  // Enhanced fields (optional for now, required later)
  sources?: Array<{
    layer: number,
    model_name: string,
    confidence: number,
    detection_time: string
  }>,
  attack_type?: string,
  attack_name?: string,
  correlation_summary?: string
}
```

---

### 3. FL Status Page (`/fl-status`)

**Current Mock Data Structure:**
```typescript
// From webapp/utils/mock-data.ts
interface FLRound {
  roundNumber: number
  progress: number
  phase: "distributing" | "training" | "aggregating" | "complete"
  timeRemaining: number  // minutes
  clientsActive: number
  totalClients: number
  epsilon: number
  modelAccuracy: number
}

interface FLClient {
  id: string
  name: string  // "Facility A", "Facility B", etc.
  status: "active" | "delayed" | "offline"
  progress: number  // 0-100
  loss: number
  accuracy: number
}

interface PrivacyMetrics {
  epsilon: number
  delta: string  // "10⁻⁵"
  dataSize: string  // "~10 MB"
  encryption: string  // "AES-256"
}

interface RoundHistoryItem {
  roundNumber: number
  status: "in-progress" | "completed" | "failed"
  duration: number  // minutes
  clients: string  // "6/6"
  accuracyChange: number | null  // +0.8%
  epsilon: number
}
```

**WebApp Features:**
- Current round progress with live updates
- 6 facility client cards with individual progress
- Privacy metrics display
- Round history table
- Trigger new FL round button

**Backend API Endpoints Needed:**

```
GET /api/fl/rounds/current
Response: {
  id: number,
  round_number: number,
  status: "in-progress" | "completed" | "failed",
  phase: "distributing" | "training" | "aggregating" | "complete",
  progress: number,  // 0-100
  time_remaining: number,  // minutes (calculated)
  start_time: string,
  end_time: string | null,
  epsilon: number,
  model_accuracy: number,
  clients_active: number,
  total_clients: number
}

GET /api/fl/clients
Response: Array<{
  id: string,
  name: string,
  facility_id: string,
  status: "active" | "delayed" | "offline",
  progress: number,
  current_epoch: number,
  total_epochs: number,
  loss: number,
  accuracy: number,
  last_update: string
}>

GET /api/fl/privacy-metrics
Response: {
  epsilon: number,
  delta: string,
  data_size: string,
  encryption: string,
  privacy_budget_remaining: number
}

GET /api/fl/rounds/history?limit=10
Response: {
  rounds: Array<{
    round_number: number,
    status: "in-progress" | "completed" | "failed",
    duration: number,  // minutes
    clients: string,  // "6/6"
    accuracy_change: number | null,
    epsilon: number,
    start_time: string,
    end_time: string
  }>
}

POST /api/fl/rounds/trigger
Response: {
  round_id: number,
  round_number: number,
  status: "started"
}
```

---

### 4. Attack Graph Page (`/attack-graph`)

**Current Mock Data Structure:**
```typescript
// From webapp/utils/attack-graph-data.ts
interface Node {
  id: string  // "T1190"
  name: string  // "Exploit Public-Facing Application"
  type: "current" | "predicted"
  probability: number  // 0.0 to 1.0
}

interface Link {
  source: string  // node id
  target: string  // node id
  probability: number
}

interface AttackGraphData {
  nodes: Node[]
  links: Link[]
}

interface TechniqueDetails {
  description: string
  detection: string
  mitigation: string
  platforms: string
  tactics: string
}
```

**WebApp Features:**
- D3.js force-directed graph
- Interactive node selection
- Technique details sidebar
- Attack timeline
- Current vs predicted highlighting

**Backend API Endpoints Needed:**

```
GET /api/mitre/graph
Response: {
  nodes: Array<{
    id: string,
    name: string,
    type: "current" | "predicted",
    probability: number
  }>,
  links: Array<{
    source: string,
    target: string,
    probability: number
  }>
}

GET /api/mitre/technique/{technique_id}
Response: {
  id: string,
  name: string,
  description: string,
  tactics: string,
  detection: string,
  mitigation: string,
  platforms: string,
  affected_assets: string[] | null
}

GET /api/predictions
Response: {
  predictions: Array<{
    id: string,
    timestamp: string,
    current_technique: string,
    current_technique_name: string,
    predicted_techniques: Array<{
      technique_id: string,
      technique_name: string,
      probability: number,
      rank: number
    }>,
    validated: boolean
  }>
}
```

---


## WebSocket Message Formats

### WebApp WebSocket Usage

**Connection:**
```typescript
// WebApp will connect to:
const ws = new WebSocket('ws://localhost:8000/ws')
```

**Expected Message Format:**
```typescript
{
  channel: "alerts" | "fl_status" | "predictions" | "system",
  type: "new" | "update" | "delete",
  data: any
}
```

### Channel: `alerts`

**Message Types:**

1. **New Alert**
```json
{
  "channel": "alerts",
  "type": "new",
  "data": {
    "id": "uuid",
    "title": "Port Scan Detected",
    "description": "...",
    "severity": "critical",
    "facility": "Facility A",
    "source": "LSTM Model",
    "timestamp": "2025-11-10T10:02:45Z",
    "status": "new",
    "relative_time": "just now"
  }
}
```

2. **Alert Updated**
```json
{
  "channel": "alerts",
  "type": "update",
  "data": {
    "id": "uuid",
    "status": "acknowledged",
    "updated_at": "2025-11-10T10:05:00Z"
  }
}
```

### Channel: `fl_status`

**Message Types:**

1. **Round Started**
```json
{
  "channel": "fl_status",
  "type": "round_started",
  "data": {
    "round_id": 42,
    "round_number": 42,
    "status": "in-progress",
    "phase": "distributing"
  }
}
```

2. **Progress Update**
```json
{
  "channel": "fl_status",
  "type": "progress_update",
  "data": {
    "round_id": 42,
    "progress": 45,
    "phase": "training",
    "time_remaining": 3
  }
}
```

3. **Client Update**
```json
{
  "channel": "fl_status",
  "type": "client_update",
  "data": {
    "client_id": "uuid",
    "name": "Facility A",
    "status": "active",
    "progress": 85,
    "current_epoch": 5,
    "loss": 0.12,
    "accuracy": 94.2
  }
}
```

4. **Round Complete**
```json
{
  "channel": "fl_status",
  "type": "round_complete",
  "data": {
    "round_id": 42,
    "round_number": 42,
    "status": "completed",
    "duration": 5.5,
    "model_accuracy": 96.2,
    "accuracy_change": 0.8
  }
}
```

### Channel: `predictions`

**Message Types:**

1. **New Prediction**
```json
{
  "channel": "predictions",
  "type": "new",
  "data": {
    "id": "uuid",
    "timestamp": "2025-11-10T10:02:17Z",
    "current_technique": "T0846",
    "current_technique_name": "Port Scan",
    "predicted_techniques": [
      {
        "technique_id": "T0800",
        "technique_name": "Lateral Movement",
        "probability": 0.72,
        "rank": 1
      }
    ]
  }
}
```

2. **Prediction Validated**
```json
{
  "channel": "predictions",
  "type": "validated",
  "data": {
    "prediction_id": "uuid",
    "validated": true,
    "actual_technique": "T0800",
    "validation_time": "2025-11-10T10:05:00Z"
  }
}
```

### Channel: `system`

**Message Types:**

1. **System Status Update**
```json
{
  "channel": "system",
  "type": "status_update",
  "data": {
    "active_alerts": 13,
    "fl_progress": 68,
    "prediction_accuracy": 89
  }
}
```

2. **Facility Status Change**
```json
{
  "channel": "system",
  "type": "facility_status",
  "data": {
    "facility_id": "facility_a",
    "name": "Facility A",
    "status": "critical",
    "alert_count": 5
  }
}
```

---

## API Response Format Standards

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": { ... }
  }
}
```

### Pagination Response
```json
{
  "success": true,
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "pages": 10
  }
}
```

---

## Data Type Mappings

### Timestamps
- **Backend**: ISO 8601 format (`2025-11-10T10:02:45Z`)
- **WebApp**: Displays as relative time ("2 min ago") using `date-fns`

**Backend should provide both:**
```json
{
  "timestamp": "2025-11-10T10:02:45Z",
  "relative_time": "2 minutes ago"
}
```

### Enums

**Severity:**
```typescript
"critical" | "high" | "medium" | "low"
```

**Status:**
```typescript
"new" | "acknowledged" | "resolved" | "false-positive"
```

**FL Phase:**
```typescript
"distributing" | "training" | "aggregating" | "complete"
```

**FL Status:**
```typescript
"in-progress" | "completed" | "failed"
```

**Client Status:**
```typescript
"active" | "delayed" | "offline"
```

**Node Type:**
```typescript
"current" | "predicted"
```

---

## WebApp Component → API Mapping

### Dashboard Components

| Component | API Endpoint | Update Method |
|-----------|-------------|---------------|
| SystemStatusCard | GET /api/system/status | WebSocket (system) |
| RecentAlertsCard | GET /api/alerts?limit=3 | WebSocket (alerts) |
| FLStatusCard | GET /api/fl/rounds/current | WebSocket (fl_status) |
| AttackPredictionCard | GET /api/predictions/latest | WebSocket (predictions) |

### Alerts Page Components

| Component | API Endpoint | Update Method |
|-----------|-------------|---------------|
| AlertTable | GET /api/alerts | REST + WebSocket |
| AlertFilters | GET /api/alerts (with params) | REST |
| AlertStats | GET /api/alerts/stats | REST + WebSocket |
| AlertDetails Modal | GET /api/alerts/{id} | REST |
| Status Update | PUT /api/alerts/{id}/status | REST |

### FL Status Page Components

| Component | API Endpoint | Update Method |
|-----------|-------------|---------------|
| RoundProgressCard | GET /api/fl/rounds/current | WebSocket (fl_status) |
| ClientStatusCards | GET /api/fl/clients | WebSocket (fl_status) |
| PrivacyMetrics | GET /api/fl/privacy-metrics | REST |
| RoundHistory | GET /api/fl/rounds/history | REST |
| Trigger Button | POST /api/fl/rounds/trigger | REST |

### Attack Graph Page Components

| Component | API Endpoint | Update Method |
|-----------|-------------|---------------|
| ForceDirectedGraph | GET /api/mitre/graph | REST + WebSocket |
| TechniqueDetails | GET /api/mitre/technique/{id} | REST |
| AttackTimeline | GET /api/predictions | WebSocket (predictions) |

---

## Environment Variables

### WebApp (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Backend (.env)
```bash
# API
API_HOST=0.0.0.0
API_PORT=8000

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Database
DATABASE_URL=postgresql://ics_user:password@localhost:5432/ics_threat_detection

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

---

## API Client Implementation (WebApp)

### Create API Client Utility

```typescript
// webapp/lib/api-client.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class APIClient {
  private baseURL: string

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`)
    if (params) {
      Object.keys(params).forEach(key => 
        url.searchParams.append(key, params[key])
      )
    }

    const response = await fetch(url.toString())
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    return response.json()
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    return response.json()
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`)
    }
    return response.json()
  }
}

export const apiClient = new APIClient(API_URL)

// Specific API methods
export const alertsAPI = {
  getAll: (params?: any) => apiClient.get('/api/alerts', params),
  getById: (id: string) => apiClient.get(`/api/alerts/${id}`),
  updateStatus: (id: string, status: string) => 
    apiClient.put(`/api/alerts/${id}/status`, { status }),
  getStats: () => apiClient.get('/api/alerts/stats')
}

export const flAPI = {
  getCurrentRound: () => apiClient.get('/api/fl/rounds/current'),
  getClients: () => apiClient.get('/api/fl/clients'),
  getPrivacyMetrics: () => apiClient.get('/api/fl/privacy-metrics'),
  getRoundHistory: (limit?: number) => 
    apiClient.get('/api/fl/rounds/history', { limit }),
  triggerRound: () => apiClient.post('/api/fl/rounds/trigger')
}

export const predictionsAPI = {
  getAll: () => apiClient.get('/api/predictions'),
  getLatest: () => apiClient.get('/api/predictions/latest'),
  getGraph: () => apiClient.get('/api/mitre/graph'),
  getTechnique: (id: string) => apiClient.get(`/api/mitre/technique/${id}`)
}

export const systemAPI = {
  getStatus: () => apiClient.get('/api/system/status'),
  getHealth: () => apiClient.get('/health')
}
```

### Create WebSocket Hook

```typescript
// webapp/hooks/use-websocket.ts

import { useEffect, useRef, useState } from 'react'

const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws'

interface WebSocketMessage {
  channel: string
  type: string
  data: any
}

export function useWebSocket(
  onMessage: (message: WebSocketMessage) => void
) {
  const ws = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    ws.current = new WebSocket(WS_URL)

    ws.current.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
    }

    ws.current.onmessage = (event) => {
      const message = JSON.parse(event.data)
      onMessage(message)
    }

    ws.current.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
    }

    ws.current.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return () => {
      ws.current?.close()
    }
  }, [onMessage])

  return { isConnected }
}
```

---

## Migration Plan: Mock Data → Real API

### Step 1: Dashboard Page

**Before:**
```typescript
const [systemStatus] = useState({
  activeAlerts: 12,
  flProgress: 67,
  predictionAccuracy: 89
})
```

**After:**
```typescript
const [systemStatus, setSystemStatus] = useState(null)
const [loading, setLoading] = useState(true)

useEffect(() => {
  systemAPI.getStatus()
    .then(data => setSystemStatus(data))
    .finally(() => setLoading(false))
}, [])

// WebSocket updates
useWebSocket((message) => {
  if (message.channel === 'system' && message.type === 'status_update') {
    setSystemStatus(message.data)
  }
})
```

### Step 2: Alerts Page

**Before:**
```typescript
import { mockAlerts } from "@/utils/mock-data"
const [alerts] = useState(mockAlerts)
```

**After:**
```typescript
const [alerts, setAlerts] = useState([])
const [loading, setLoading] = useState(true)

useEffect(() => {
  alertsAPI.getAll({ page: currentPage, limit: 10, ...filters })
    .then(response => setAlerts(response.alerts))
    .finally(() => setLoading(false))
}, [currentPage, filters])

// WebSocket for real-time updates
useWebSocket((message) => {
  if (message.channel === 'alerts') {
    if (message.type === 'new') {
      setAlerts(prev => [message.data, ...prev])
    } else if (message.type === 'update') {
      setAlerts(prev => prev.map(alert => 
        alert.id === message.data.id ? { ...alert, ...message.data } : alert
      ))
    }
  }
})
```

### Step 3: FL Status Page

**Before:**
```typescript
import { mockFLRound, mockFLClients } from "@/utils/mock-data"
const [currentRound] = useState(mockFLRound)
const [clients] = useState(mockFLClients)
```

**After:**
```typescript
const [currentRound, setCurrentRound] = useState(null)
const [clients, setClients] = useState([])

useEffect(() => {
  Promise.all([
    flAPI.getCurrentRound(),
    flAPI.getClients()
  ]).then(([round, clientsData]) => {
    setCurrentRound(round)
    setClients(clientsData)
  })
}, [])

// WebSocket for live updates
useWebSocket((message) => {
  if (message.channel === 'fl_status') {
    if (message.type === 'progress_update') {
      setCurrentRound(prev => ({ ...prev, ...message.data }))
    } else if (message.type === 'client_update') {
      setClients(prev => prev.map(client =>
        client.id === message.data.client_id ? { ...client, ...message.data } : client
      ))
    }
  }
})
```

### Step 4: Attack Graph Page

**Before:**
```typescript
import { mockAttackGraphData } from "@/utils/attack-graph-data"
const [graphData] = useState(mockAttackGraphData)
```

**After:**
```typescript
const [graphData, setGraphData] = useState({ nodes: [], links: [] })

useEffect(() => {
  predictionsAPI.getGraph()
    .then(data => setGraphData(data))
}, [])

// WebSocket for prediction updates
useWebSocket((message) => {
  if (message.channel === 'predictions' && message.type === 'new') {
    // Update graph with new prediction
    predictionsAPI.getGraph().then(data => setGraphData(data))
  }
})
```

---

## Testing Checklist

### API Endpoints
- [ ] All endpoints return correct data structure
- [ ] Pagination works correctly
- [ ] Filtering works correctly
- [ ] Search works correctly
- [ ] Error handling returns proper error format

### WebSocket
- [ ] Connection establishes successfully
- [ ] Messages received in correct format
- [ ] All channels working (alerts, fl_status, predictions, system)
- [ ] Reconnection works after disconnect

### WebApp Integration
- [ ] Dashboard loads data correctly
- [ ] Alerts page displays and filters correctly
- [ ] FL status page shows live updates
- [ ] Attack graph renders correctly
- [ ] Real-time updates appear without refresh

### End-to-End
- [ ] Create alert → appears in webapp
- [ ] Trigger FL round → progress updates live
- [ ] Generate prediction → graph updates
- [ ] Update alert status → reflects immediately

---

**Document Version:** 1.0  
**Last Updated:** November 10, 2025  
**Status:** API-WebApp Alignment Specification
