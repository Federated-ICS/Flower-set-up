"""
IsolationForest-based anomaly detector.
"""
import numpy as np
import pickle
import logging
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


class IsolationForestDetector:
    """
    Anomaly detector using sklearn's IsolationForest.
    """
    
    def __init__(self, contamination=0.1, random_state=42):
        """
        Initialize the IsolationForest detector.
        
        Args:
            contamination: Expected proportion of outliers in the dataset
            random_state: Random seed for reproducibility
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100
        )
        self.contamination = contamination
        
    def train(self, X_train, y_train=None):
        """
        Train the IsolationForest model.
        
        Args:
            X_train: Training features
            y_train: Training labels (not used by IsolationForest but kept for consistency)
        
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training IsolationForest with {len(X_train)} samples")
        self.model.fit(X_train)
        
        # Evaluate on training data
        metrics = self.evaluate(X_train, y_train) if y_train is not None else {}
        logger.info(f"Training completed. Metrics: {metrics}")
        return metrics
    
    def predict(self, X):
        """
        Predict anomalies.
        
        Args:
            X: Feature array
        
        Returns:
            Predictions where 1=anomaly, 0=normal
        """
        # IsolationForest returns -1 for anomalies and 1 for normal
        predictions = self.model.predict(X)
        # Convert to 0/1 format (0=normal, 1=anomaly)
        predictions = np.where(predictions == -1, 1, 0)
        return predictions
    
    def evaluate(self, X_test, y_test):
        """
        Evaluate the model on test data.
        
        Args:
            X_test: Test features
            y_test: Test labels
        
        Returns:
            Dictionary containing accuracy, precision, recall, and F1 score
        """
        predictions = self.predict(X_test)
        
        metrics = {
            'accuracy': accuracy_score(y_test, predictions),
            'precision': precision_score(y_test, predictions, zero_division=0),
            'recall': recall_score(y_test, predictions, zero_division=0),
            'f1_score': f1_score(y_test, predictions, zero_division=0)
        }
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
    
    def save_model(self, filepath):
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
        """
        with open(filepath, 'wb') as f:
            pickle.dump(self.model, f)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load the model from disk.
        
        Args:
            filepath: Path to load the model from
        """
        with open(filepath, 'rb') as f:
            self.model = pickle.load(f)
        logger.info(f"Model loaded from {filepath}")
    
    def get_parameters(self):
        """
        Get model parameters (for federated learning).
        Note: IsolationForest doesn't have traditional weights,
        so we return a serialized version of the model.
        
        Returns:
            List containing serialized model
        """
        return [pickle.dumps(self.model)]
    
    def set_parameters(self, parameters):
        """
        Set model parameters (for federated learning).
        
        Args:
            parameters: List containing serialized model
        """
        if parameters:
            self.model = pickle.loads(parameters[0])
