"""
Flower client implementation for federated learning.
"""
import logging
import flwr as fl
import numpy as np

logger = logging.getLogger(__name__)


class AnomalyDetectorClient(fl.client.NumPyClient):
    """
    Flower client for anomaly detection models.
    """
    
    def __init__(self, model, X_train, y_train, X_test, y_test, client_id):
        """
        Initialize the Flower client.
        
        Args:
            model: Anomaly detector model (IsolationForest or LSTM Autoencoder)
            X_train: Training features for this client
            y_train: Training labels for this client
            X_test: Test features for this client
            y_test: Test labels for this client
            client_id: Unique identifier for this client
        """
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.client_id = client_id
        
        logger.info(f"Client {client_id} initialized with {len(X_train)} training samples and {len(X_test)} test samples")
    
    def get_parameters(self, config):
        """
        Get model parameters.
        
        Args:
            config: Configuration dictionary
        
        Returns:
            Model parameters as a list of numpy arrays
        """
        logger.info(f"Client {self.client_id}: Getting parameters")
        return self.model.get_parameters()
    
    def fit(self, parameters, config):
        """
        Train the model on local data.
        
        Args:
            parameters: Model parameters from the server
            config: Configuration dictionary
        
        Returns:
            Updated parameters, number of training samples, and metrics
        """
        logger.info(f"Client {self.client_id}: Starting training round")
        
        # Set model parameters
        self.model.set_parameters(parameters)
        
        # Train the model
        train_metrics = self.model.train(self.X_train, self.y_train)
        
        # Log training metrics
        logger.info(f"Client {self.client_id}: Training metrics: {train_metrics}")
        
        # Return updated parameters and metrics
        return self.model.get_parameters(), len(self.X_train), train_metrics
    
    def evaluate(self, parameters, config):
        """
        Evaluate the model on local test data.
        
        Args:
            parameters: Model parameters from the server
            config: Configuration dictionary
        
        Returns:
            Loss, number of test samples, and evaluation metrics
        """
        logger.info(f"Client {self.client_id}: Starting evaluation")
        
        # Set model parameters
        self.model.set_parameters(parameters)
        
        # Evaluate the model
        metrics = self.model.evaluate(self.X_test, self.y_test)
        
        # Log evaluation metrics
        logger.info(f"Client {self.client_id}: Evaluation metrics: {metrics}")
        
        # Return loss (using negative F1 as loss), number of samples, and metrics
        loss = 1.0 - metrics.get('f1_score', 0.0)
        
        return loss, len(self.X_test), metrics


def create_client(model, X_train, y_train, X_test, y_test, client_id):
    """
    Factory function to create a Flower client.
    
    Args:
        model: Anomaly detector model
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels
        client_id: Client identifier
    
    Returns:
        AnomalyDetectorClient instance
    """
    return AnomalyDetectorClient(model, X_train, y_train, X_test, y_test, client_id)
