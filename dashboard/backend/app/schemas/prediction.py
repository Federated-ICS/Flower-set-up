from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class PredictedTechniqueSchema(BaseModel):
    technique_id: str
    technique_name: str
    probability: float
    rank: int
    timeframe: Optional[str] = None

    class Config:
        from_attributes = True


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
    validation_time: Optional[datetime] = None
    predicted_techniques: List[PredictedTechniqueSchema] = []

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
