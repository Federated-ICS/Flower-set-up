"""FastAPI backend entrypoint."""
from __future__ import annotations

import asyncio
from typing import List

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from .config import get_settings
from .database import Base, async_session, engine
from .kafka_ingestor import KafkaIngestor
from . import models, schemas

settings = get_settings()
app = FastAPI(title="Federated Attack Detection Backend", version="1.0.0")
kafka_ingestor = KafkaIngestor()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await kafka_ingestor.start()


@app.on_event("shutdown")
async def on_shutdown():
    await kafka_ingestor.stop()


@app.get("/anomalies", response_model=List[schemas.AnomalySchema])
async def list_anomalies(limit: int = 50, session: AsyncSession = Depends(get_session)):
    stmt = select(models.AnomalyRecord).order_by(desc(models.AnomalyRecord.created_at)).limit(limit)
    results = (await session.execute(stmt)).scalars().all()
    return results


@app.get("/classifications", response_model=List[schemas.ClassificationSchema])
async def list_classifications(limit: int = 50, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(models.AttackClassificationRecord)
        .order_by(desc(models.AttackClassificationRecord.created_at))
        .limit(limit)
    )
    results = (await session.execute(stmt)).scalars().all()
    return results


@app.get("/predictions", response_model=List[schemas.PredictionSchema])
async def list_predictions(limit: int = 50, session: AsyncSession = Depends(get_session)):
    stmt = (
        select(models.AttackPredictionRecord)
        .order_by(desc(models.AttackPredictionRecord.created_at))
        .limit(limit)
    )
    results = (await session.execute(stmt)).scalars().all()
    return results


@app.get("/alerts", response_model=List[schemas.AlertSchema])
async def list_alerts(limit: int = 50, session: AsyncSession = Depends(get_session)):
    stmt = select(models.AlertRecord).order_by(desc(models.AlertRecord.created_at)).limit(limit)
    results = (await session.execute(stmt)).scalars().all()
    return results


@app.get("/fl-events", response_model=List[schemas.FLEventSchema])
async def list_fl_events(limit: int = 50, session: AsyncSession = Depends(get_session)):
    stmt = select(models.FLEventRecord).order_by(desc(models.FLEventRecord.created_at)).limit(limit)
    results = (await session.execute(stmt)).scalars().all()
    return results


@app.websocket("/ws/events")
async def websocket_events(socket: WebSocket):
    queue: asyncio.Queue = asyncio.Queue()
    await socket.accept()
    kafka_ingestor.register_listener(queue)
    try:
        while True:
            event = await queue.get()
            await socket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        kafka_ingestor.unregister_listener(queue)
