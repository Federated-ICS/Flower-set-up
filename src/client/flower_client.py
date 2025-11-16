"""
Flower client implementation for federated learning.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import flwr as fl
import numpy as np

from streaming.fl_events import RoundMetricPublisher

logger = logging.getLogger(__name__)


@dataclass
class DifferentialPrivacyConfig:
    """DP hyper-parameters for Flower clients."""

    clipping_norm: float = 1.0
    noise_multiplier: float = 0.3
    delta: float = 1e-5


class AnomalyDetectorClient(fl.client.NumPyClient):
    """
    Flower client for anomaly detection models with DP noise and Kafka logging.
    """

    def __init__(
        self,
        model,
        X_train,
        y_train,
        X_test,
        y_test,
        client_id,
        dp_config: Optional[DifferentialPrivacyConfig] = None,
    ):
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.client_id = client_id
        self.dp_config = dp_config or DifferentialPrivacyConfig()
        self.epsilon_spent = 0.0
        self.metric_publisher = RoundMetricPublisher()

        logger.info(
            "Client %s initialized with %s training samples and %s test samples",
            client_id,
            len(X_train),
            len(X_test),
        )

    # DP helpers ----------------------------------------------------------
    def _clip_and_noise(self, weights: List[np.ndarray]) -> List[np.ndarray]:
        dp_weights: List[np.ndarray] = []
        for tensor in weights:
            norm = np.linalg.norm(tensor)
            clip = self.dp_config.clipping_norm
            if norm > clip:
                tensor = tensor * (clip / (norm + 1e-12))
            noise = np.random.normal(
                loc=0.0,
                scale=self.dp_config.noise_multiplier * clip,
                size=tensor.shape,
            )
            dp_weights.append(tensor + noise)
        # update simplistic epsilon accounting
        self.epsilon_spent += clip / max(self.dp_config.noise_multiplier, 1e-6)
        return dp_weights

    def _publish_metrics(self, metrics: Dict, round_id: int, loss: float = 0.0):
        payload = metrics.copy()
        payload["loss"] = loss
        self.metric_publisher.publish(
            payload,
            role="client",
            node_id=str(self.client_id),
            round_id=round_id,
            epsilon=self.epsilon_spent,
            delta=self.dp_config.delta,
        )

    # Flower interface ----------------------------------------------------
    def get_parameters(self, config):
        logger.info("Client %s: Getting parameters", self.client_id)
        params = self.model.get_parameters()
        return params

    def fit(self, parameters, config):
        logger.info("Client %s: Starting training round", self.client_id)
        round_id = config.get("server_round", 0)

        self.model.set_parameters(parameters)
        train_metrics = self.model.train(self.X_train, self.y_train)
        loss = 1.0 - train_metrics.get("f1_score", 0.0)

        logger.info("Client %s: Training metrics: %s", self.client_id, train_metrics)

        dp_params = self._clip_and_noise(self.model.get_parameters())
        self._publish_metrics(train_metrics, round_id=round_id, loss=loss)

        return dp_params, len(self.X_train), train_metrics

    def evaluate(self, parameters, config):
        logger.info("Client %s: Starting evaluation", self.client_id)
        round_id = config.get("server_round", 0)

        self.model.set_parameters(parameters)
        metrics = self.model.evaluate(self.X_test, self.y_test)
        loss = 1.0 - metrics.get("f1_score", 0.0)

        logger.info("Client %s: Evaluation metrics: %s", self.client_id, metrics)
        self._publish_metrics(metrics, round_id=round_id, loss=loss)

        return loss, len(self.X_test), metrics


def create_client(model, X_train, y_train, X_test, y_test, client_id, dp_config=None):
    """
    Factory function to create a Flower client.
    """
    return AnomalyDetectorClient(model, X_train, y_train, X_test, y_test, client_id, dp_config=dp_config)
