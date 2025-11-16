"""
Synthetic network flow generator producing events to Kafka.
"""
from __future__ import annotations

import logging
import os
import random
import sys
import time
import uuid
from typing import List

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data.data_generation import generate_dataset
from streaming.event_models import NetworkPacket
from streaming.kafka_config import DEFAULT_TOPICS, load_settings
from streaming.kafka_utils import build_producer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("network-simulator")


class NetworkSimulator:
    def __init__(self, sleep_interval: float = 0.5):
        self.settings = load_settings(prefix="SIM")
        self.topic = DEFAULT_TOPICS["network_data"]
        self.producer = build_producer(self.settings)
        self.sleep_interval = sleep_interval
        self.X, self.y = generate_dataset(n_normal=900, n_anomalous=100, n_features=10, random_state=42)
        self.cursor = 0

    def _random_ip(self):
        return ".".join(str(random.randint(0, 255)) for _ in range(4))

    def _build_packet(self, features: List[float]) -> dict:
        return NetworkPacket(
            flow_id=str(uuid.uuid4()),
            src_ip=self._random_ip(),
            dst_ip=self._random_ip(),
            protocol=random.choice(["tcp", "udp"]),
            src_port=random.randint(1024, 65535),
            dst_port=random.randint(1, 1024),
            payload_size=float(np.random.lognormal(mean=3, sigma=1)),
            features=list(map(float, features)),
            metadata={"label": str(int(self.y[self.cursor]))},
        ).to_dict()

    def run(self):
        logger.info("Network simulator started, streaming to topic %s", self.topic)
        try:
            while True:
                features = self.X[self.cursor % len(self.X)]
                packet = self._build_packet(features)
                self.producer.send(self.topic, packet)
                self.producer.flush()

                self.cursor += 1
                time.sleep(self.sleep_interval)
        except KeyboardInterrupt:
            logger.info("Simulator stopped via keyboard interrupt")
        finally:
            self.producer.flush()
            self.producer.close()


if __name__ == "__main__":
    NetworkSimulator().run()
