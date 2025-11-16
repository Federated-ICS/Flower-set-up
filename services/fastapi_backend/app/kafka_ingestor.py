"""Background Kafka consumer persisting events into PostgreSQL."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict

from aiokafka import AIOKafkaConsumer

from streaming.kafka_config import DEFAULT_TOPICS

from .config import get_settings
from .database import async_session
from . import models

logger = logging.getLogger("fastapi-backend.kafka")


class KafkaIngestor:
    def __init__(self):
        self.settings = get_settings()
        self.running = False
        self.consumer: AIOKafkaConsumer | None = None
        self.listeners: set[asyncio.Queue] = set()
        self.handlers = {
            DEFAULT_TOPICS["anomalies"]: self._handle_anomaly,
            DEFAULT_TOPICS["attack_classified"]: self._handle_classification,
            DEFAULT_TOPICS["attack_predicted"]: self._handle_prediction,
            DEFAULT_TOPICS["alerts"]: self._handle_alert,
            DEFAULT_TOPICS["fl_events"]: self._handle_fl_event,
        }

    async def start(self):
        if self.consumer:
            return
        topics = list(self.handlers.keys())
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.settings.kafka_bootstrap_servers,
            group_id=self.settings.kafka_group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=True,
            auto_offset_reset="latest",
        )
        await self.consumer.start()
        self.running = True
        asyncio.create_task(self._consume())
        logger.info("Kafka ingestor subscribed to %s", topics)

    async def stop(self):
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

    async def _consume(self):
        assert self.consumer is not None
        try:
            async for msg in self.consumer:
                handler = self.handlers.get(msg.topic)
                if handler:
                    await handler(msg.value)
        except asyncio.CancelledError:  # pragma: no cover
            pass
        finally:
            await self.stop()

    def register_listener(self, queue: asyncio.Queue):
        self.listeners.add(queue)

    def unregister_listener(self, queue: asyncio.Queue):
        self.listeners.discard(queue)

    async def _broadcast(self, event_type: str, payload: Dict[str, Any]):
        for queue in list(self.listeners):
            await queue.put({"type": event_type, "payload": payload})

    # Handlers ------------------------------------------------------------
    async def _handle_anomaly(self, payload: Dict[str, Any]):
        async with async_session() as session:
            record = models.AnomalyRecord(
                flow_id=payload.get("flow_id", ""),
                detector=payload.get("detector", ""),
                score=payload.get("score", 0.0),
                is_anomaly=payload.get("is_anomaly", False),
                context=payload.get("context", {}),
            )
            session.add(record)
            await session.commit()
        await self._broadcast("anomaly", payload)

    async def _handle_classification(self, payload: Dict[str, Any]):
        async with async_session() as session:
            record = models.AttackClassificationRecord(
                flow_id=payload.get("flow_id", ""),
                label=payload.get("label", ""),
                probabilities=payload.get("probabilities", {}),
                supporting_detectors=payload.get("supporting_detectors", []),
            )
            session.add(record)
            await session.commit()
        await self._broadcast("attack_classification", payload)

    async def _handle_prediction(self, payload: Dict[str, Any]):
        async with async_session() as session:
            record = models.AttackPredictionRecord(
                flow_id=payload.get("flow_id", ""),
                severity=payload.get("severity", 0.0),
                impacted_nodes=payload.get("impacted_nodes", []),
                explanation=payload.get("explanation", ""),
            )
            session.add(record)
            await session.commit()
        await self._broadcast("attack_prediction", payload)

    async def _handle_alert(self, payload: Dict[str, Any]):
        async with async_session() as session:
            record = models.AlertRecord(
                flow_id=payload.get("flow_id", ""),
                title=payload.get("title", ""),
                severity=payload.get("severity", ""),
                summary=payload.get("summary", ""),
                source=payload.get("source", ""),
                payload=payload.get("payload", {}),
            )
            session.add(record)
            await session.commit()
        await self._broadcast("alert", payload)

    async def _handle_fl_event(self, payload: Dict[str, Any]):
        async with async_session() as session:
            record = models.FLEventRecord(
                round_id=payload.get("round_id", 0),
                role=payload.get("role", ""),
                node_id=payload.get("node_id", ""),
                accuracy=payload.get("accuracy", 0.0),
                precision=payload.get("precision", 0.0),
                recall=payload.get("recall", 0.0),
                f1_score=payload.get("f1_score", 0.0),
                loss=payload.get("loss", 0.0),
                epsilon=payload.get("epsilon"),
                delta=payload.get("delta"),
                extra=payload.get("extra", {}),
            )
            session.add(record)
            await session.commit()
        await self._broadcast("fl_event", payload)
