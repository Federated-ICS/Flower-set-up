"""
Helpers for publishing Flower round metrics to Kafka.
"""
from __future__ import annotations

import logging
from contextlib import AbstractContextManager
from typing import Dict, Optional

from kafka import KafkaProducer

from .event_models import FLEvent
from .kafka_config import KafkaSettings, load_settings
from .kafka_utils import build_producer, publish_event

logger = logging.getLogger(__name__)


class RoundMetricPublisher(AbstractContextManager):
    """
    Context manager around a Kafka producer dedicated to FL metrics.
    """

    def __init__(self, topic: str = "fl_events", settings: Optional[KafkaSettings] = None):
        self.settings = settings or load_settings(prefix="FL")
        self.topic = topic
        self.producer: KafkaProducer | None = None

    def __enter__(self):
        self.producer = build_producer(self.settings)
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        if self.producer:
            self.producer.flush()
            self.producer.close()

    def publish(
        self,
        payload: Dict,
        role: str,
        node_id: str,
        round_id: int,
        epsilon: Optional[float] = None,
        delta: Optional[float] = None,
    ) -> None:
        if not self.producer:
            self.producer = build_producer(self.settings)

        event = FLEvent(
            role=role,
            node_id=node_id,
            round_id=round_id,
            accuracy=payload.get("accuracy", 0.0),
            precision=payload.get("precision", 0.0),
            recall=payload.get("recall", 0.0),
            f1_score=payload.get("f1_score", 0.0),
            loss=payload.get("loss", 0.0),
            epsilon=epsilon,
            delta=delta,
            extra={k: str(v) for k, v in payload.items() if k not in {"accuracy", "precision", "recall", "f1_score", "loss"}},
        ).to_dict()

        publish_event(self.producer, self.topic, event)
        logger.debug("FL metric published: %s", event)
