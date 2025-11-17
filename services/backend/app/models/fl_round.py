import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class RoundStatusEnum(str, enum.Enum):
    in_progress = "in-progress"
    completed = "completed"
    failed = "failed"


class PhaseEnum(str, enum.Enum):
    distributing = "distributing"
    training = "training"
    aggregating = "aggregating"
    complete = "complete"


class ClientStatusEnum(str, enum.Enum):
    active = "active"
    delayed = "delayed"
    offline = "offline"


class FLRound(Base):
    __tablename__ = "fl_rounds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_number = Column(Integer, unique=True, nullable=False, index=True)
    status: RoundStatusEnum = Column(  # type: ignore
        Enum(RoundStatusEnum), nullable=False, default=RoundStatusEnum.in_progress
    )
    phase: PhaseEnum = Column(  # type: ignore
        Enum(PhaseEnum), nullable=False, default=PhaseEnum.distributing
    )

    start_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_time = Column(DateTime)

    progress = Column(Integer, default=0)  # 0-100
    epsilon = Column(Float, default=0.5)
    model_accuracy = Column(Float)

    clients_active = Column(Integer, default=0)
    total_clients = Column(Integer, default=6)

    # Relationships
    clients = relationship("FLClient", back_populates="round", cascade="all, delete-orphan")


class FLClient(Base):
    __tablename__ = "fl_clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    round_id = Column(Integer, ForeignKey("fl_rounds.id", ondelete="CASCADE"))

    facility_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    status: ClientStatusEnum = Column(  # type: ignore
        Enum(ClientStatusEnum), nullable=False, default=ClientStatusEnum.active
    )

    progress = Column(Integer, default=0)  # 0-100
    current_epoch = Column(Integer, default=0)
    total_epochs = Column(Integer, default=10)

    loss = Column(Float)
    accuracy = Column(Float)

    last_update = Column(DateTime, default=datetime.utcnow)

    # Relationship
    round = relationship("FLRound", back_populates="clients")
