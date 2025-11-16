from typing import List, Optional

from pydantic import BaseModel


class TechniqueNode(BaseModel):
    id: str
    name: str
    type: str  # "current" or "predicted"
    probability: float


class TechniqueLink(BaseModel):
    source: str
    target: str
    probability: float


class AttackGraph(BaseModel):
    nodes: List[TechniqueNode]
    links: List[TechniqueLink]


class TechniqueDetails(BaseModel):
    id: str
    name: str
    description: str
    detection: Optional[str] = None
    mitigation: Optional[str] = None
    platforms: List[str]
    tactics: List[str]
