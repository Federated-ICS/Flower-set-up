import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class NetworkData(Base):
    __tablename__ = "network_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    facility_id = Column(String, nullable=False, index=True)

    # Aggregated metrics
    packets_per_sec = Column(Integer)
    bytes_per_sec = Column(Integer)
    unique_src_ips = Column(Integer)
    unique_dest_ips = Column(Integer)
    protocol_distribution = Column(Float)
    failed_connections = Column(Integer)
    avg_packet_size = Column(Integer)
    inter_arrival_time = Column(Integer)

    # Raw features (JSON for flexibility)
    raw_features = Column(JSON)
