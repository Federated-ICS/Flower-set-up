"""
Base anomaly detection Kafka microservice.
"""
from __future__ import annotations

import logging
from typing import Dict, Tuple

import numpy as np

from streaming.event_models import AnomalyEvent
from streaming.kafka_config import DEFAULT_TOPICS
from .base_service import StreamingService

logger = logging.getLogger(__name__)


class BaseAnomalyService(StreamingService):
    def __init__(self, detector_name: str, **kwargs):
        super().__init__(
            service_name=detector_name,
            input_topics=[DEFAULT_TOPICS["network_data"]],
            output_topic=DEFAULT_TOPICS["anomalies"],
            **kwargs,
        )
        self.detector_name = detector_name

    def parse_features(self, payload: Dict) -> np.ndarray:
        feats = payload.get("features")
        if feats is None:
            raise ValueError("Missing features in payload")
        return np.array(feats).reshape(1, -1)

    def score(self, features: np.ndarray, payload: Dict) -> Tuple[float, bool, Dict]:
        raise NotImplementedError

    def handle_message(self, payload):
        try:
            features = self.parse_features(payload)
        except ValueError:
            logger.warning("%s skipping payload without features: %s", self.detector_name, payload)
            return

        score, is_anomaly, context = self.score(features, payload)
        event = AnomalyEvent(
            detector=self.detector_name,
            flow_id=payload.get("flow_id", ""),
            score=float(score),
            is_anomaly=is_anomaly,
            features=payload.get("features", []),
            context=context,
        ).to_dict()
        self.emit(event)
        logger.debug("%s emitted anomaly event %s", self.detector_name, event)
