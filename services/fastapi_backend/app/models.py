"""SQLAlchemy models for persisted events."""
from __future__ import annotations

from datetime import datetime
from typing import Dict

from sqlalchemy import JSON, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class AnomalyRecord(TimestampMixin, Base):
    __tablename__ = "anomalies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flow_id: Mapped[str] = mapped_column(String(128))
    detector: Mapped[str] = mapped_column(String(64))
    score: Mapped[float] = mapped_column(Float)
    is_anomaly: Mapped[bool] = mapped_column()
    context: Mapped[Dict] = mapped_column(JSON)


class AttackClassificationRecord(TimestampMixin, Base):
    __tablename__ = "attack_classifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flow_id: Mapped[str] = mapped_column(String(128))
    label: Mapped[str] = mapped_column(String(32))
    probabilities: Mapped[Dict] = mapped_column(JSON)
    supporting_detectors: Mapped[Dict] = mapped_column(JSON)


class AttackPredictionRecord(TimestampMixin, Base):
    __tablename__ = "attack_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flow_id: Mapped[str] = mapped_column(String(128))
    severity: Mapped[float] = mapped_column(Float)
    impacted_nodes: Mapped[Dict] = mapped_column(JSON)
    explanation: Mapped[str] = mapped_column(String(512))


class FLEventRecord(TimestampMixin, Base):
    __tablename__ = "fl_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(32))
    node_id: Mapped[str] = mapped_column(String(32))
    accuracy: Mapped[float] = mapped_column(Float)
    precision: Mapped[float] = mapped_column(Float)
    recall: Mapped[float] = mapped_column(Float)
    f1_score: Mapped[float] = mapped_column(Float)
    loss: Mapped[float] = mapped_column(Float)
    epsilon: Mapped[float | None] = mapped_column(Float, nullable=True)
    delta: Mapped[float | None] = mapped_column(Float, nullable=True)
    extra: Mapped[Dict] = mapped_column(JSON)


class AlertRecord(TimestampMixin, Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    flow_id: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(128))
    severity: Mapped[str] = mapped_column(String(16))
    summary: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(64))
    payload: Mapped[Dict] = mapped_column(JSON)
