"""
Main script to run Flower federated learning clients.
"""
import logging
import sys
import os
import argparse
import numpy as np

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import flwr as fl
from data.data_generation import generate_dataset, split_data_for_clients
from models.isolation_forest_detector import IsolationForestDetector
from models.lstm_autoencoder_detector import LSTMAutoencoderDetector
from client.flower_client import AnomalyDetectorClient


def setup_logging(client_id):
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'client_{client_id}.log')
        ]
    )


def main():
    parser = argparse.ArgumentParser(description='Run Flower federated learning client')
    parser.add_argument('--client-id', type=int, required=True, help='Client ID (0, 1, or 2)')
    parser.add_argument('--model-type', type=str, choices=['isolation_forest', 'lstm_autoencoder'], 
                       default='lstm_autoencoder', help='Type of anomaly detector model')
    parser.add_argument('--server-address', type=str, default='localhost:8080', 
                       help='Server address')
    
    args = parser.parse_args()
    
    setup_logging(args.client_id)
    logger = logging.getLogger(__name__)
    
    logger.info("="*50)
    logger.info(f"Starting Federated Learning Client {args.client_id}")
    logger.info("="*50)
    
    # Generate data
    logger.info("Generating synthetic data...")
    X, y = generate_dataset(n_normal=900, n_anomalous=100, n_features=10, random_state=42)
    
    # Split data for clients
    client_data = split_data_for_clients(X, y, n_clients=3, random_state=42)
    
    # Get data for this client
    X_client, y_client = client_data[args.client_id]
    
    # Split into train and test
    split_idx = int(0.8 * len(X_client))
    X_train, X_test = X_client[:split_idx], X_client[split_idx:]
    y_train, y_test = y_client[:split_idx], y_client[split_idx:]
    
    logger.info(f"Client {args.client_id} data: {len(X_train)} train, {len(X_test)} test samples")
    logger.info(f"Training data - Normal: {np.sum(y_train == 0)}, Anomalous: {np.sum(y_train == 1)}")
    logger.info(f"Test data - Normal: {np.sum(y_test == 0)}, Anomalous: {np.sum(y_test == 1)}")
    
    # Create model
    logger.info(f"Creating {args.model_type} model...")
    if args.model_type == 'isolation_forest':
        model = IsolationForestDetector(contamination=0.1, random_state=42)
    else:  # lstm_autoencoder
        model = LSTMAutoencoderDetector(n_features=10, latent_dim=5, sequence_length=1)
    
    # Create client
    client = AnomalyDetectorClient(model, X_train, y_train, X_test, y_test, args.client_id)
    
    # Start client
    logger.info(f"Connecting to server at {args.server_address}...")
    fl.client.start_numpy_client(
        server_address=args.server_address,
        client=client
    )
    
    logger.info(f"Client {args.client_id} finished")
    
    # Save the final model
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f"client_{args.client_id}_{args.model_type}")
    model.save_model(model_path)
    logger.info(f"Final model saved to {model_path}")


if __name__ == "__main__":
    main()
