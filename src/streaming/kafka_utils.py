"""
Helpers for constructing Kafka producers/consumers with consistent settings.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, Iterable, Optional

from kafka import KafkaConsumer, KafkaProducer

from .kafka_config import KafkaSettings, load_settings

logger = logging.getLogger(__name__)


def build_producer(settings: Optional[KafkaSettings] = None, **overrides: Any) -> KafkaProducer:
    cfg = settings or load_settings()
    producer = KafkaProducer(
        bootstrap_servers=cfg.bootstrap_servers,
        security_protocol=cfg.security_protocol,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        **overrides,
    )
    return producer


def build_consumer(
    topics: Iterable[str],
    settings: Optional[KafkaSettings] = None,
    **overrides: Any,
) -> KafkaConsumer:
    cfg = settings or load_settings()
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=cfg.bootstrap_servers,
        group_id=cfg.group_id,
        security_protocol=cfg.security_protocol,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        **overrides,
    )
    return consumer


def publish_event(producer: KafkaProducer, topic: str, payload: Dict[str, Any]) -> None:
    """Publish and log errors."""
    try:
        producer.send(topic, payload)
        producer.flush()
    except Exception:  # pragma: no cover - logging branch
        logger.exception("Failed to publish payload to topic %s", topic)
