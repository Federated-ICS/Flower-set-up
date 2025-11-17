from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel


class FLClientSchema(BaseModel):
    id: UUID
    facility_id: str
    name: str
    status: Literal["active", "delayed", "offline"]
    progress: int
    current_epoch: int
    total_epochs: int
    loss: Optional[float] = None
    accuracy: Optional[float] = None
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
    end_time: Optional[datetime] = None
    progress: int
    epsilon: float
    model_accuracy: Optional[float] = None
    clients_active: int
    total_clients: int
    clients: List[FLClientSchema] = []
    time_remaining: Optional[int] = None  # minutes

    class Config:
        from_attributes = True


class PrivacyMetrics(BaseModel):
    epsilon: float
    delta: str
    data_size: str
    encryption: str
    privacy_budget_remaining: float


class RoundHistoryItem(BaseModel):
    round_number: int
    status: Literal["in-progress", "completed", "failed"]
    duration: Optional[float] = None  # minutes
    clients: str  # "6/6"
    accuracy_change: Optional[float] = None
    epsilon: float
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True
