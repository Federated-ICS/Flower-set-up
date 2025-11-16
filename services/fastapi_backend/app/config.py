"""Application settings."""
from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@postgres:5432/attacks"
    )
    kafka_bootstrap_servers: str = Field(default="kafka:9092")
    kafka_group_id: str = Field(default="fastapi-backend")
    kafka_topics: dict = Field(
        default={
            "network": "network_data",
            "anomalies": "anomalies",
            "classified": "attack_classified",
            "predicted": "attack_predicted",
            "alerts": "alerts",
            "fl": "fl_events",
        }
    )

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
