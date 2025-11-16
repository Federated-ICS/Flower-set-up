"""
Kafka microservice wrapping the LSTM Autoencoder anomaly detector.
"""
from __future__ import annotations

import logging
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data.data_generation import generate_dataset
from models.lstm_autoencoder_detector import LSTMAutoencoderDetector
from streaming.services.anomaly_service import BaseAnomalyService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-lstm")


class LSTMAnomalyService(BaseAnomalyService):
    def __init__(self):
        logger.info("Training LSTM autoencoder for streaming service bootstrap")
        X, y = generate_dataset(n_normal=600, n_anomalous=80, n_features=10, random_state=7)
        self.detector = LSTMAutoencoderDetector(n_features=X.shape[1], latent_dim=5, sequence_length=1)
        self.detector.train(X, y, epochs=5, batch_size=64)
        super().__init__(detector_name="anomaly_lstm")

    def score(self, features: np.ndarray, payload):
        reconstruction_input = self.detector._reshape_data(features)  # pylint: disable=protected-access
        reconstructions = self.detector.model.predict(reconstruction_input, verbose=0)
        mse = float(np.mean(np.power(reconstruction_input - reconstructions, 2)))
        threshold = float(self.detector.threshold or 0.0)
        is_anomaly = mse > threshold
        return mse, is_anomaly, {"threshold": f"{threshold:.4f}"}


if __name__ == "__main__":
    LSTMAnomalyService().run()
