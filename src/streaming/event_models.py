"""
Dataclasses describing the JSON payloads exchanged via Kafka topics.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


@dataclass
class EventBase:
    event_type: str
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class NetworkPacket(EventBase):
    event_type: str = "network_packet"
    flow_id: str = ""
    src_ip: str = ""
    dst_ip: str = ""
    protocol: str = "tcp"
    src_port: int = 0
    dst_port: int = 0
    payload_size: float = 0.0
    features: List[float] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class AnomalyEvent(EventBase):
    event_type: str = "anomaly"
    detector: str = ""
    flow_id: str = ""
    score: float = 0.0
    is_anomaly: bool = False
    features: List[float] = field(default_factory=list)
    context: Dict[str, str] = field(default_factory=dict)


@dataclass
class AttackClassification(EventBase):
    event_type: str = "attack_classification"
    classifier: str = "threat_classifier"
    flow_id: str = ""
    label: str = ""
    probabilities: Dict[str, float] = field(default_factory=dict)
    supporting_detectors: List[str] = field(default_factory=list)


@dataclass
class AttackPrediction(EventBase):
    event_type: str = "attack_prediction"
    predictor: str = "gnn_predictor"
    flow_id: str = ""
    severity: float = 0.0
    impacted_nodes: List[str] = field(default_factory=list)
    next_hop: Optional[str] = None
    explanation: str = ""


@dataclass
class AlertEvent(EventBase):
    event_type: str = "alert"
    flow_id: str = ""
    title: str = ""
    severity: str = "medium"
    summary: str = ""
    source: str = ""
    payload: Dict[str, str] = field(default_factory=dict)


@dataclass
class FLEvent(EventBase):
    event_type: str = "fl_event"
    round_id: int = 0
    role: str = "server"
    node_id: str = ""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    loss: float = 0.0
    epsilon: Optional[float] = None
    delta: Optional[float] = None
    extra: Dict[str, str] = field(default_factory=dict)
