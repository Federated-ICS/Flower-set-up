"""
LSTM Autoencoder-based anomaly detector using TensorFlow/Keras.
"""
import numpy as np
import logging
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

logger = logging.getLogger(__name__)


class LSTMAutoencoderDetector:
    """
    Anomaly detector using LSTM Autoencoder.
    """
    
    def __init__(self, n_features=10, latent_dim=5, sequence_length=1):
        """
        Initialize the LSTM Autoencoder detector.
        
        Args:
            n_features: Number of input features
            latent_dim: Dimension of the latent representation
            sequence_length: Length of input sequences
        """
        self.n_features = n_features
        self.latent_dim = latent_dim
        self.sequence_length = sequence_length
        self.model = self._build_model()
        self.threshold = None
        
    def _build_model(self):
        """
        Build the LSTM Autoencoder model.
        
        Returns:
            Compiled Keras model
        """
        # Encoder
        encoder_inputs = keras.Input(shape=(self.sequence_length, self.n_features))
        encoder_lstm = layers.LSTM(self.latent_dim, return_sequences=False)(encoder_inputs)
        
        # Decoder
        decoder_lstm = layers.RepeatVector(self.sequence_length)(encoder_lstm)
        decoder_lstm = layers.LSTM(self.latent_dim, return_sequences=True)(decoder_lstm)
        decoder_outputs = layers.TimeDistributed(layers.Dense(self.n_features))(decoder_lstm)
        
        # Autoencoder model
        autoencoder = keras.Model(encoder_inputs, decoder_outputs)
        autoencoder.compile(optimizer='adam', loss='mse')
        
        logger.info(f"LSTM Autoencoder model built with {self.n_features} features and {self.latent_dim} latent dimensions")
        return autoencoder
    
    def _reshape_data(self, X):
        """
        Reshape data to fit LSTM input requirements.
        
        Args:
            X: Input data of shape (n_samples, n_features)
        
        Returns:
            Reshaped data of shape (n_samples, sequence_length, n_features)
        """
        if len(X.shape) == 2:
            return X.reshape((X.shape[0], self.sequence_length, self.n_features))
        return X
    
    def train(self, X_train, y_train=None, epochs=50, batch_size=32, validation_split=0.1):
        """
        Train the LSTM Autoencoder model.
        
        Args:
            X_train: Training features
            y_train: Training labels (used for threshold calculation)
            epochs: Number of training epochs
            batch_size: Batch size for training
            validation_split: Fraction of training data to use for validation
        
        Returns:
            Training metrics dictionary
        """
        logger.info(f"Training LSTM Autoencoder with {len(X_train)} samples")
        
        # Reshape data for LSTM
        X_train_reshaped = self._reshape_data(X_train)
        
        # Train autoencoder (unsupervised)
        history = self.model.fit(
            X_train_reshaped, X_train_reshaped,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=0
        )
        
        # Calculate reconstruction error threshold on normal data
        if y_train is not None:
            normal_indices = np.where(y_train == 0)[0]
            if len(normal_indices) > 0:
                X_normal = X_train_reshaped[normal_indices]
                reconstructions = self.model.predict(X_normal, verbose=0)
                mse = np.mean(np.power(X_normal - reconstructions, 2), axis=(1, 2))
                self.threshold = np.percentile(mse, 95)  # 95th percentile as threshold
            else:
                # If no normal samples, use all data
                reconstructions = self.model.predict(X_train_reshaped, verbose=0)
                mse = np.mean(np.power(X_train_reshaped - reconstructions, 2), axis=(1, 2))
                self.threshold = np.percentile(mse, 90)
        else:
            # If no labels, use all data
            reconstructions = self.model.predict(X_train_reshaped, verbose=0)
            mse = np.mean(np.power(X_train_reshaped - reconstructions, 2), axis=(1, 2))
            self.threshold = np.percentile(mse, 90)
        
        logger.info(f"Training completed. Loss: {history.history['loss'][-1]:.4f}, Threshold: {self.threshold:.4f}")
        
        # Evaluate on training data if labels provided
        metrics = {}
        if y_train is not None:
            metrics = self.evaluate(X_train, y_train)
            
        return metrics
    
    def predict(self, X):
        """
        Predict anomalies based on reconstruction error.
        
        Args:
            X: Feature array
        
        Returns:
            Predictions where 1=anomaly, 0=normal
        """
        X_reshaped = self._reshape_data(X)
        reconstructions = self.model.predict(X_reshaped, verbose=0)
        mse = np.mean(np.power(X_reshaped - reconstructions, 2), axis=(1, 2))
        
        if self.threshold is None:
            # If threshold not set, use median
            self.threshold = np.median(mse)
        
        predictions = (mse > self.threshold).astype(int)
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
            filepath: Path to save the model (without extension)
        """
        # Add .keras extension if not present
        if not filepath.endswith('.keras') and not filepath.endswith('.h5'):
            filepath = filepath + '.keras'
        self.model.save(filepath)
        # Save threshold separately
        threshold_path = filepath + '_threshold.npy'
        np.save(threshold_path, self.threshold)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """
        Load the model from disk.
        
        Args:
            filepath: Path to load the model from (without extension)
        """
        # Add .keras extension if not present
        if not filepath.endswith('.keras') and not filepath.endswith('.h5'):
            filepath = filepath + '.keras'
        self.model = keras.models.load_model(filepath)
        # Load threshold
        threshold_path = filepath.replace('.keras', '_threshold.npy').replace('.h5', '_threshold.npy')
        try:
            self.threshold = np.load(threshold_path)
        except:
            logger.warning("Threshold file not found, will be recalculated on next training")
            self.threshold = None
        logger.info(f"Model loaded from {filepath}")
    
    def get_parameters(self):
        """
        Get model parameters (for federated learning).
        
        Returns:
            List of model weights
        """
        return self.model.get_weights()
    
    def set_parameters(self, parameters):
        """
        Set model parameters (for federated learning).
        
        Args:
            parameters: List of model weights
        """
        self.model.set_weights(parameters)
