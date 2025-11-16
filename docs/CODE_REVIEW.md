# Code Review Notes

## Scope
Initial scan of the Flower federated learning components and the FastAPI Kafka ingestor.

## Findings
- **Differential privacy accounting is placeholder-level.** `AnomalyDetectorClient` increments `epsilon_spent` with `clip / noise_multiplier` per round, which does not follow any formal DP accounting or track composition across training epochs. This risks misrepresenting the privacy budget in logs and downstream dashboards. Consider using a moments accountant or Opacus/TensorFlow Privacy utilities to compute epsilon based on the actual mechanism, noise, sampling, and round count. (See `src/client/flower_client.py`, `_clip_and_noise`).
- **Kafka ingestor lacks resilience to consumer failures.** The background `_consume` loop only tolerates `asyncio.CancelledError`; any other exception will tear down the consumer and stop ingestion without retries or logging. Introducing explicit exception handling and restart logic would make the FastAPI backend more robust to broker hiccups or malformed payloads. (See `services/fastapi_backend/app/kafka_ingestor.py`, `_consume`).
- **Backpressure in event fan-out can stall ingestion.** `_broadcast` awaits queue puts sequentially for every listener, so one slow or dead websocket queue can block all others and delay database commits. Using `asyncio.Queue.put_nowait` with error handling or scheduling sends as tasks would prevent a single consumer from backpressuring the entire ingest path. (See `services/fastapi_backend/app/kafka_ingestor.py`, `_broadcast`).
