from datetime import datetime
from typing import Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class AlertSourceSchema(BaseModel):
    layer: int
    model_name: str
    confidence: float
    detection_time: datetime
    evidence: str
    context_evidence: Optional[Dict] = None

    class Config:
        from_attributes = True


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
    sources: List[AlertSourceSchema] = []
    correlation_confidence: Optional[float] = None
    correlation_summary: Optional[str] = None
    attack_type: Optional[str] = None
    attack_name: Optional[str] = None
    context_analysis: Optional[ContextAnalysis] = None
    relative_time: Optional[str] = None

    class Config:
        from_attributes = True


class AlertUpdate(BaseModel):
    status: Literal["acknowledged", "resolved", "false-positive"]


class AlertStats(BaseModel):
    total: int
    critical: int
    unresolved: int
    false_positives: int
