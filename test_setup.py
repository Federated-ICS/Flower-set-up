"""
Simple test to verify basic functionality of the federated learning setup.
This test verifies data generation, models, and basic client setup without
running the actual federated learning server.
"""
import sys
import os
import logging

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_generation import generate_dataset, split_data_for_clients
from models.isolation_forest_detector import IsolationForestDetector
from models.lstm_autoencoder_detector import LSTMAutoencoderDetector
from client.flower_client import AnomalyDetectorClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_data_generation():
    """Test data generation functionality."""
    logger.info("Testing data generation...")
    X, y = generate_dataset(n_normal=900, n_anomalous=100, n_features=10, random_state=42)
    assert X.shape == (1000, 10), f"Expected shape (1000, 10), got {X.shape}"
    assert y.shape == (1000,), f"Expected shape (1000,), got {y.shape}"
    assert sum(y == 0) == 900, f"Expected 900 normal samples, got {sum(y == 0)}"
    assert sum(y == 1) == 100, f"Expected 100 anomalous samples, got {sum(y == 1)}"
    logger.info("✓ Data generation test passed")
    return X, y


def test_data_splitting(X, y):
    """Test data splitting for clients."""
    logger.info("Testing data splitting...")
    client_data = split_data_for_clients(X, y, n_clients=3, random_state=42)
    assert len(client_data) == 3, f"Expected 3 clients, got {len(client_data)}"
    total_samples = sum(len(X_c) for X_c, _ in client_data)
    assert total_samples == len(X), f"Expected {len(X)} total samples, got {total_samples}"
    logger.info("✓ Data splitting test passed")
    return client_data


def test_isolation_forest(X, y):
    """Test IsolationForest detector."""
    logger.info("Testing IsolationForest detector...")
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    model = IsolationForestDetector(contamination=0.1, random_state=42)
    train_metrics = model.train(X_train, y_train)
    test_metrics = model.evaluate(X_test, y_test)
    
    assert 'accuracy' in train_metrics, "Missing accuracy in training metrics"
    assert 'f1_score' in test_metrics, "Missing f1_score in test metrics"
    assert 0 <= test_metrics['accuracy'] <= 1, f"Invalid accuracy: {test_metrics['accuracy']}"
    
    logger.info(f"  Train metrics: {train_metrics}")
    logger.info(f"  Test metrics: {test_metrics}")
    logger.info("✓ IsolationForest test passed")


def test_lstm_autoencoder(X, y):
    """Test LSTM Autoencoder detector."""
    logger.info("Testing LSTM Autoencoder detector...")
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    model = LSTMAutoencoderDetector(n_features=10, latent_dim=5, sequence_length=1)
    train_metrics = model.train(X_train, y_train, epochs=5, batch_size=32)
    test_metrics = model.evaluate(X_test, y_test)
    
    assert 'accuracy' in train_metrics, "Missing accuracy in training metrics"
    assert 'f1_score' in test_metrics, "Missing f1_score in test metrics"
    assert 0 <= test_metrics['accuracy'] <= 1, f"Invalid accuracy: {test_metrics['accuracy']}"
    
    logger.info(f"  Train metrics: {train_metrics}")
    logger.info(f"  Test metrics: {test_metrics}")
    logger.info("✓ LSTM Autoencoder test passed")


def test_client_creation(client_data):
    """Test Flower client creation."""
    logger.info("Testing Flower client creation...")
    X_client, y_client = client_data[0]
    split_idx = int(0.8 * len(X_client))
    X_train, X_test = X_client[:split_idx], X_client[split_idx:]
    y_train, y_test = y_client[:split_idx], y_client[split_idx:]
    
    model = IsolationForestDetector(contamination=0.1, random_state=42)
    client = AnomalyDetectorClient(model, X_train, y_train, X_test, y_test, client_id=0)
    
    # Test get_parameters
    params = client.get_parameters(config={})
    assert params is not None, "Failed to get parameters"
    
    logger.info("✓ Client creation test passed")


def main():
    """Run all tests."""
    logger.info("="*60)
    logger.info("Running Federated Learning Setup Tests")
    logger.info("="*60)
    
    try:
        # Test data generation
        X, y = test_data_generation()
        
        # Test data splitting
        client_data = test_data_splitting(X, y)
        
        # Test IsolationForest
        test_isolation_forest(X, y)
        
        # Test LSTM Autoencoder
        test_lstm_autoencoder(X, y)
        
        # Test client creation
        test_client_creation(client_data)
        
        logger.info("="*60)
        logger.info("✓ ALL TESTS PASSED")
        logger.info("="*60)
        return 0
        
    except Exception as e:
        logger.error(f"✗ TEST FAILED: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
