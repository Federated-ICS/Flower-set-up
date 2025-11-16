"""
Centralized Kafka configuration helpers.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List


DEFAULT_TOPICS = {
    "network_data": "network_data",
    "anomalies": "anomalies",
    "attack_classified": "attack_classified",
    "attack_predicted": "attack_predicted",
    "alerts": "alerts",
    "fl_events": "fl_events",
}


@dataclass(frozen=True)
class KafkaSettings:
    """Runtime Kafka settings loaded from environment variables."""

    bootstrap_servers: str = "kafka:9092"
    security_protocol: str = "PLAINTEXT"
    group_id: str | None = None
    topics: dict[str, str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.topics is None:
            object.__setattr__(self, "topics", DEFAULT_TOPICS.copy())

    @property
    def all_topics(self) -> List[str]:
        return list(self.topics.values())


def load_settings(prefix: str | None = None, group_id: str | None = None) -> KafkaSettings:
    """
    Load Kafka settings from environment variables.

    Args:
        prefix: Optional prefix for bootstrap env var (e.g. FL, BACKEND)
        group_id: Optional consumer group id override
    """
    env_prefix = f"{prefix.upper()}_" if prefix else ""
    bootstrap = os.getenv(f"{env_prefix}KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    security_protocol = os.getenv(f"{env_prefix}KAFKA_SECURITY_PROTOCOL", "PLAINTEXT")

    return KafkaSettings(
        bootstrap_servers=bootstrap,
        security_protocol=security_protocol,
        group_id=group_id or os.getenv(f"{env_prefix}KAFKA_GROUP_ID"),
    )
