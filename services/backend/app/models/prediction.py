import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    current_technique = Column(String, nullable=False)
    current_technique_name = Column(String, nullable=False)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id"))

    validated = Column(Boolean, default=False)
    validation_time = Column(DateTime)

    # Relationships
    predicted_techniques = relationship(
        "PredictedTechnique", back_populates="prediction", cascade="all, delete-orphan"
    )


class PredictedTechnique(Base):
    __tablename__ = "predicted_techniques"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.id", ondelete="CASCADE"))

    technique_id = Column(String, nullable=False)  # e.g., "T0800"
    technique_name = Column(String, nullable=False)
    probability = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    timeframe = Column(String)  # e.g., "15-60 minutes"

    # Relationship
    prediction = relationship("Prediction", back_populates="predicted_techniques")
