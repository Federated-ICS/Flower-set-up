"""
Graph-based threat predictor consuming classified attacks.
"""
from __future__ import annotations

import logging
import os
import random
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from streaming.event_models import AlertEvent, AttackPrediction
from streaming.kafka_config import DEFAULT_TOPICS
from streaming.kafka_utils import build_producer
from streaming.services.base_service import StreamingService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("severity-predictor")


class GNNPredictorService(StreamingService):
    def __init__(self):
        super().__init__(
            service_name="severity_predictor",
            input_topics=[DEFAULT_TOPICS["attack_classified"]],
            output_topic=DEFAULT_TOPICS["attack_predicted"],
        )
        self.alert_topic = DEFAULT_TOPICS["alerts"]
        self.alert_producer = build_producer(self.settings)

    def _severity(self, probs):
        dos = probs.get("dos", 0.0)
        probe = probs.get("probe", 0.0)
        return min(1.0, 0.6 * dos + 0.4 * probe + random.uniform(0, 0.15))

    def handle_message(self, payload):
        flow_id = payload.get("flow_id", "")
        probs = payload.get("probabilities", {})
        severity = self._severity(probs)
        nodes = [payload.get("src_ip", "edge"), payload.get("dst_ip", "core")]
        next_hop = nodes[-1]
        explanation = f"Combined anomaly votes -> {payload.get('label')}."

        prediction = AttackPrediction(
            flow_id=flow_id,
            severity=severity,
            impacted_nodes=nodes,
            next_hop=next_hop,
            explanation=explanation,
        ).to_dict()
        self.emit(prediction)
        logger.debug("Severity predictor emitted %s", prediction)

        if severity > 0.65:
            alert = AlertEvent(
                flow_id=flow_id,
                title="High severity attack forecast",
                severity="high" if severity > 0.8 else "medium",
                summary=f"GNN forecast severity {severity:.2f} ({payload.get('label', 'unknown')})",
                source="severity_predictor",
                payload={"probabilities": str(probs)},
            ).to_dict()
            self.alert_producer.send(self.alert_topic, alert)
            self.alert_producer.flush()


if __name__ == "__main__":
    GNNPredictorService().run()
