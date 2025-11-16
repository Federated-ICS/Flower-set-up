"""
Threat classification service consuming anomalies and emitting attack labels.
"""
from __future__ import annotations

import logging
import os
import sys
from collections import defaultdict, deque
from statistics import mean
from typing import Deque, Dict, List

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from streaming.event_models import AttackClassification
from streaming.kafka_config import DEFAULT_TOPICS
from streaming.services.base_service import StreamingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("threat-classifier")


class ThreatClassifierService(StreamingService):
    def __init__(self):
        super().__init__(
            service_name="threat_classifier",
            input_topics=[DEFAULT_TOPICS["anomalies"]],
            output_topic=DEFAULT_TOPICS["attack_classified"],
        )
        self.window: Dict[str, Deque[Dict]] = defaultdict(lambda: deque(maxlen=5))

    def _classify(self, flow_id: str, findings: List[Dict]) -> AttackClassification:
        scores = [f["score"] for f in findings]
        avg_score = mean(scores) if scores else 0.0
        vote_count = len(findings)
        severity = avg_score if avg_score >= 0 else 0.0

        if avg_score > 12 or vote_count >= 3:
            label = "dos"
            probs = {"dos": min(1.0, avg_score / 15), "probe": 0.2, "benign": 0.05}
        elif avg_score > 6:
            label = "probe"
            probs = {"dos": 0.3, "probe": min(1.0, avg_score / 10), "benign": 0.2}
        else:
            label = "benign"
            probs = {"dos": 0.1, "probe": 0.2, "benign": 0.7}

        supporting = [f["detector"] for f in findings]

        return AttackClassification(
            flow_id=flow_id,
            label=label,
            probabilities=probs,
            supporting_detectors=supporting,
        )

    def handle_message(self, payload):
        flow_id = payload.get("flow_id")
        if not flow_id:
            return

        self.window[flow_id].append(
            {"detector": payload.get("detector"), "score": payload.get("score", 0.0)}
        )

        # classify when enough votes gathered
        if len(self.window[flow_id]) >= 2:
            event = self._classify(flow_id, list(self.window[flow_id]))
            self.emit(event.to_dict())
            logger.debug("Threat classifier emitted %s", event)
            # drop processed votes
            self.window.pop(flow_id, None)


if __name__ == "__main__":
    ThreatClassifierService().run()
