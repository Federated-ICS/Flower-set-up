"""Pydantic response models."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class AnomalySchema(BaseModel):
    flow_id: str
    detector: str
    score: float
    is_anomaly: bool
    context: Dict
    created_at: datetime


class ClassificationSchema(BaseModel):
    flow_id: str
    label: str
    probabilities: Dict[str, float]
    supporting_detectors: List[str]
    created_at: datetime


class PredictionSchema(BaseModel):
    flow_id: str
    severity: float
    impacted_nodes: List[str]
    explanation: str
    created_at: datetime


class AlertSchema(BaseModel):
    flow_id: str
    title: str
    severity: str
    summary: str
    source: str
    payload: Dict
    created_at: datetime


class FLEventSchema(BaseModel):
    round_id: int
    role: str
    node_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    loss: float
    epsilon: Optional[float]
    delta: Optional[float]
    created_at: datetime
