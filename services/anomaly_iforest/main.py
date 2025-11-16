"""
Kafka microservice for IsolationForest-based anomaly detection.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data.data_generation import generate_dataset
from models.isolation_forest_detector import IsolationForestDetector
from streaming.services.anomaly_service import BaseAnomalyService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-iforest")


class IsolationForestService(BaseAnomalyService):
    def __init__(self):
        logger.info("Bootstrapping IsolationForest detector for streaming service")
        X, y = generate_dataset(n_normal=600, n_anomalous=80, n_features=10, random_state=13)
        self.detector = IsolationForestDetector(contamination=0.12, random_state=13)
        self.detector.train(X, y)
        super().__init__(detector_name="anomaly_iforest")

    def score(self, features: np.ndarray, payload):
        prediction = self.detector.predict(features)[0]
        confidence = float(np.clip(self.detector.model.decision_function(features)[0], -1, 1))
        is_anomaly = bool(prediction == 1)
        return confidence, is_anomaly, {"decision_score": f"{confidence:.4f}"}


if __name__ == "__main__":
    IsolationForestService().run()
