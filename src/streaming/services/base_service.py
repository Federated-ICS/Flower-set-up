"""
Reusable Kafka streaming service base.
"""
from __future__ import annotations

import logging
import signal
from typing import Iterable

from kafka import KafkaConsumer, KafkaProducer

from streaming.kafka_config import KafkaSettings, load_settings
from streaming.kafka_utils import build_consumer, build_producer

logger = logging.getLogger(__name__)


class StreamingService:
    """Simple base class that wires Kafka producer/consumer lifecycle."""

    def __init__(
        self,
        service_name: str,
        input_topics: Iterable[str],
        output_topic: str | None = None,
        kafka_settings: KafkaSettings | None = None,
    ):
        self.service_name = service_name
        self.settings = kafka_settings or load_settings(prefix=service_name.upper(), group_id=f"{service_name}-group")
        self.consumer: KafkaConsumer = build_consumer(input_topics, settings=self.settings)
        self.producer: KafkaProducer | None = build_producer(self.settings) if output_topic else None
        self.output_topic = output_topic
        self._running = True

        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        logger.info("%s received signal %s, shutting down", self.service_name, signum)
        self._running = False

    def run(self):
        logger.info("%s service started", self.service_name)
        for message in self.consumer:
            if not self._running:
                break
            try:
                self.handle_message(message.value)
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("%s failed handling payload %s", self.service_name, message.value)

        self.consumer.close()
        if self.producer:
            self.producer.flush()
            self.producer.close()
        logger.info("%s service stopped", self.service_name)

    # To be implemented ---------------------------------------------------
    def handle_message(self, payload):
        raise NotImplementedError

    def emit(self, payload):
        if not self.output_topic or not self.producer:
            raise RuntimeError(f"{self.service_name} has no configured output topic")
        self.producer.send(self.output_topic, payload)
        self.producer.flush()
