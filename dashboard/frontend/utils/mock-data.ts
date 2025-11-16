// Mock alert data for development
export interface Alert {
  id: string
  title: string
  description: string
  severity: "critical" | "high" | "medium" | "low"
  facility: string
  source: string
  timestamp: string
  status: "new" | "acknowledged" | "resolved" | "false-positive"
  relativeTime: string
}

export const mockAlerts: Alert[] = [
  {
    id: "1",
    title: "Suspicious Login Attempt",
    description: "Multiple failed login attempts detected from unusual geographic location",
    severity: "critical",
    facility: "Facility A",
    source: "LSTM Model",
    timestamp: "2024-01-15T14:23:00Z",
    status: "new",
    relativeTime: "2 min ago",
  },
  {
    id: "2",
    title: "Unusual Network Traffic",
    description: "Large data exfiltration detected on internal network segment",
    severity: "high",
    facility: "Facility B",
    source: "Isolation Forest",
    timestamp: "2024-01-15T14:08:00Z",
    status: "acknowledged",
    relativeTime: "15 min ago",
  },
  {
    id: "3",
    title: "Certificate Expiration Warning",
    description: "SSL certificate expiring in 30 days, renewal recommended",
    severity: "low",
    facility: "Facility C",
    source: "System Monitor",
    timestamp: "2024-01-15T13:15:00Z",
    status: "acknowledged",
    relativeTime: "1 hour ago",
  },
  {
    id: "4",
    title: "DDoS Attack Detected",
    description: "Distributed denial of service attack blocked by firewall",
    severity: "critical",
    facility: "Facility A",
    source: "Physics Model",
    timestamp: "2024-01-15T11:20:00Z",
    status: "resolved",
    relativeTime: "3 hours ago",
  },
  {
    id: "5",
    title: "Malware Signature Match",
    description: "Known malware signature detected in file upload",
    severity: "high",
    facility: "Facility B",
    source: "LSTM Model",
    timestamp: "2024-01-15T10:45:00Z",
    status: "false-positive",
    relativeTime: "4 hours ago",
  },
  {
    id: "6",
    title: "Privilege Escalation Attempt",
    description: "User attempted to escalate privileges without authorization",
    severity: "high",
    facility: "Facility A",
    source: "System Monitor",
    timestamp: "2024-01-15T09:30:00Z",
    status: "resolved",
    relativeTime: "5 hours ago",
  },
  {
    id: "7",
    title: "Configuration Change Detected",
    description: "Unauthorized configuration change on production server",
    severity: "medium",
    facility: "Facility C",
    source: "System Monitor",
    timestamp: "2024-01-15T08:15:00Z",
    status: "acknowledged",
    relativeTime: "6 hours ago",
  },
  {
    id: "8",
    title: "Failed Authentication Event",
    description: "Multiple authentication failures detected",
    severity: "medium",
    facility: "Facility B",
    source: "LSTM Model",
    timestamp: "2024-01-15T07:00:00Z",
    status: "new",
    relativeTime: "7 hours ago",
  },
  {
    id: "9",
    title: "Unusual Database Query",
    description: "Database query pattern does not match historical baseline",
    severity: "medium",
    facility: "Facility A",
    source: "Isolation Forest",
    timestamp: "2024-01-14T20:45:00Z",
    status: "acknowledged",
    relativeTime: "18 hours ago",
  },
  {
    id: "10",
    title: "Service Availability Issue",
    description: "Service response time exceeds threshold",
    severity: "low",
    facility: "Facility C",
    source: "System Monitor",
    timestamp: "2024-01-14T15:30:00Z",
    status: "resolved",
    relativeTime: "1 day ago",
  },
  {
    id: "11",
    title: "Firewall Rule Bypass",
    description: "Traffic detected bypassing firewall rules",
    severity: "critical",
    facility: "Facility B",
    source: "Physics Model",
    timestamp: "2024-01-14T12:15:00Z",
    status: "acknowledged",
    relativeTime: "1 day ago",
  },
  {
    id: "12",
    title: "Memory Usage Spike",
    description: "Process memory usage spike detected",
    severity: "low",
    facility: "Facility A",
    source: "System Monitor",
    timestamp: "2024-01-14T10:00:00Z",
    status: "resolved",
    relativeTime: "1 day ago",
  },
  {
    id: "13",
    title: "SQL Injection Attempt",
    description: "Potential SQL injection pattern detected in web request",
    severity: "high",
    facility: "Facility C",
    source: "LSTM Model",
    timestamp: "2024-01-13T22:30:00Z",
    status: "resolved",
    relativeTime: "2 days ago",
  },
  {
    id: "14",
    title: "Port Scan Activity",
    description: "Unusual port scanning activity detected",
    severity: "high",
    facility: "Facility A",
    source: "Isolation Forest",
    timestamp: "2024-01-13T18:45:00Z",
    status: "acknowledged",
    relativeTime: "2 days ago",
  },
  {
    id: "15",
    title: "Backup Failure",
    description: "Scheduled backup failed to complete",
    severity: "low",
    facility: "Facility B",
    source: "System Monitor",
    timestamp: "2024-01-13T14:20:00Z",
    status: "resolved",
    relativeTime: "2 days ago",
  },
  {
    id: "16",
    title: "Anomalous API Usage",
    description: "API endpoint usage pattern differs from baseline",
    severity: "medium",
    facility: "Facility C",
    source: "LSTM Model",
    timestamp: "2024-01-12T19:00:00Z",
    status: "acknowledged",
    relativeTime: "3 days ago",
  },
  {
    id: "17",
    title: "SSL/TLS Handshake Failure",
    description: "Multiple TLS handshake failures detected",
    severity: "high",
    facility: "Facility A",
    source: "System Monitor",
    timestamp: "2024-01-12T15:30:00Z",
    status: "resolved",
    relativeTime: "3 days ago",
  },
  {
    id: "18",
    title: "Zombie Process Detected",
    description: "Orphaned process detected running in background",
    severity: "low",
    facility: "Facility B",
    source: "System Monitor",
    timestamp: "2024-01-12T11:00:00Z",
    status: "false-positive",
    relativeTime: "3 days ago",
  },
  {
    id: "19",
    title: "Brute Force Attack",
    description: "Rapid login attempts detected from single IP address",
    severity: "critical",
    facility: "Facility C",
    source: "LSTM Model",
    timestamp: "2024-01-11T20:15:00Z",
    status: "resolved",
    relativeTime: "4 days ago",
  },
  {
    id: "20",
    title: "DNS Tunneling Detected",
    description: "Unusual DNS query patterns suggesting data exfiltration",
    severity: "high",
    facility: "Facility A",
    source: "Isolation Forest",
    timestamp: "2024-01-11T16:45:00Z",
    status: "acknowledged",
    relativeTime: "4 days ago",
  },
]

// Mock Federated Learning data for development
export interface FLRound {
  roundNumber: number
  progress: number
  phase: "distributing" | "training" | "aggregating" | "complete"
  timeRemaining: number
  clientsActive: number
  totalClients: number
  epsilon: number
  modelAccuracy: number
}

export interface FLClient {
  id: string
  name: string
  status: "active" | "delayed" | "offline"
  progress: number
  loss: number
  accuracy: number
}

export interface PrivacyMetrics {
  epsilon: number
  delta: string
  dataSize: string
  encryption: string
}

export interface RoundHistoryItem {
  roundNumber: number
  status: "in-progress" | "completed" | "failed"
  duration: number
  clients: string
  accuracyChange: number | null
  epsilon: number
}

export const mockFLRound: FLRound = {
  roundNumber: 42,
  progress: 67,
  phase: "training",
  timeRemaining: 12,
  clientsActive: 5,
  totalClients: 6,
  epsilon: 0.82,
  modelAccuracy: 92.5,
}

export const mockFLClients: FLClient[] = [
  {
    id: "client-1",
    name: "Facility A",
    status: "active",
    progress: 85,
    loss: 0.12,
    accuracy: 94.2,
  },
  {
    id: "client-2",
    name: "Facility B",
    status: "active",
    progress: 72,
    loss: 0.18,
    accuracy: 91.8,
  },
  {
    id: "client-3",
    name: "Facility C",
    status: "delayed",
    progress: 45,
    loss: 0.25,
    accuracy: 88.5,
  },
  {
    id: "client-4",
    name: "Facility D",
    status: "active",
    progress: 91,
    loss: 0.09,
    accuracy: 95.1,
  },
  {
    id: "client-5",
    name: "Facility E",
    status: "active",
    progress: 68,
    loss: 0.21,
    accuracy: 90.3,
  },
  {
    id: "client-6",
    name: "Facility F",
    status: "active",
    progress: 78,
    loss: 0.15,
    accuracy: 92.9,
  },
]

export const mockPrivacyMetrics: PrivacyMetrics = {
  epsilon: 0.82,
  delta: "10⁻⁵",
  dataSize: "~10 MB",
  encryption: "AES-256",
}

export const mockRoundHistory: RoundHistoryItem[] = [
  {
    roundNumber: 41,
    status: "completed",
    duration: 28,
    clients: "6/6",
    accuracyChange: 0.8,
    epsilon: 0.75,
  },
  {
    roundNumber: 40,
    status: "completed",
    duration: 32,
    clients: "6/6",
    accuracyChange: -0.2,
    epsilon: 0.68,
  },
  {
    roundNumber: 39,
    status: "completed",
    duration: 25,
    clients: "5/6",
    accuracyChange: 1.2,
    epsilon: 0.61,
  },
  {
    roundNumber: 38,
    status: "failed",
    duration: 15,
    clients: "4/6",
    accuracyChange: null,
    epsilon: 0.54,
  },
]
