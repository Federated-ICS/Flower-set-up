"""
Physics-inspired deterministic anomaly detection service.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from streaming.services.anomaly_service import BaseAnomalyService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-physics")


class PhysicsRuleService(BaseAnomalyService):
    def __init__(self):
        super().__init__(detector_name="anomaly_physics")

    def score(self, features: np.ndarray, payload):
        payload_size = float(payload.get("payload_size", 0.0))
        src_port = int(payload.get("src_port", 0))
        dst_port = int(payload.get("dst_port", 0))
        energy = np.linalg.norm(features)
        surge = payload_size > 8000 or energy > 25
        impossible_port = src_port < 1024 and dst_port < 1024
        is_anomaly = surge or impossible_port
        score = float(energy + payload_size / 1000.0)
        context = {
            "payload_size": str(payload_size),
            "energy": f"{energy:.2f}",
            "rule": "surge" if surge else "port" if impossible_port else "normal",
        }
        return score, is_anomaly, context


if __name__ == "__main__":
    PhysicsRuleService().run()
