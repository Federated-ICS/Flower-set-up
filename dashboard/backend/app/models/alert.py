import enum
import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class SeverityEnum(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class StatusEnum(str, enum.Enum):
    new = "new"
    acknowledged = "acknowledged"
    resolved = "resolved"
    false_positive = "false-positive"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    facility_id = Column(String, nullable=False, index=True)
    severity: SeverityEnum = Column(Enum(SeverityEnum), nullable=False, index=True)  # type: ignore
    title = Column(String, nullable=False)
    description = Column(Text)
    status: StatusEnum = Column(  # type: ignore
        Enum(StatusEnum), nullable=False, default=StatusEnum.new, index=True
    )

    # Attack classification
    attack_type = Column(String)  # e.g., "T0846"
    attack_name = Column(String)  # e.g., "Port Scan"

    # Correlation
    correlation_confidence = Column(Float)
    correlation_summary = Column(String)

    # Context analysis (JSON)
    context_analysis = Column(JSON)

    # Relationships
    sources = relationship("AlertSource", back_populates="alert", cascade="all, delete-orphan")


class AlertSource(Base):
    __tablename__ = "alert_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"))

    layer = Column(Integer)  # 1, 2, or 3
    model_name = Column(String)  # "LSTM", "Isolation Forest", etc.
    confidence = Column(Float)
    detection_time = Column(DateTime, default=datetime.utcnow)
    evidence = Column(Text)
    context_evidence = Column(JSON)

    # Relationship
    alert = relationship("Alert", back_populates="sources")
