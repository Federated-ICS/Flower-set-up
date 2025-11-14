"""
Data generation module for synthetic normal and anomalous data.
"""
import numpy as np


def generate_normal_data(n_samples=1000, n_features=10, random_state=None):
    """
    Generate synthetic normal data.
    
    Args:
        n_samples: Number of samples to generate
        n_features: Number of features
        random_state: Random seed for reproducibility
    
    Returns:
        numpy array of shape (n_samples, n_features)
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate normal data from Gaussian distribution
    data = np.random.randn(n_samples, n_features)
    return data


def generate_anomalous_data(n_samples=100, n_features=10, random_state=None):
    """
    Generate synthetic anomalous data.
    
    Args:
        n_samples: Number of anomalous samples to generate
        n_features: Number of features
        random_state: Random seed for reproducibility
    
    Returns:
        numpy array of shape (n_samples, n_features)
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    # Generate anomalous data with higher variance and shifted mean
    data = np.random.randn(n_samples, n_features) * 3 + 5
    return data


def generate_dataset(n_normal=1000, n_anomalous=100, n_features=10, random_state=None):
    """
    Generate a complete dataset with normal and anomalous samples.
    
    Args:
        n_normal: Number of normal samples
        n_anomalous: Number of anomalous samples
        n_features: Number of features
        random_state: Random seed for reproducibility
    
    Returns:
        X: Feature array of shape (n_normal + n_anomalous, n_features)
        y: Label array where 0=normal, 1=anomalous
    """
    normal_data = generate_normal_data(n_normal, n_features, random_state)
    anomalous_data = generate_anomalous_data(n_anomalous, n_features, random_state)
    
    X = np.vstack([normal_data, anomalous_data])
    y = np.hstack([np.zeros(n_normal), np.ones(n_anomalous)])
    
    # Shuffle the data
    if random_state is not None:
        np.random.seed(random_state)
    indices = np.random.permutation(len(X))
    X = X[indices]
    y = y[indices]
    
    return X, y


def split_data_for_clients(X, y, n_clients=3, random_state=None):
    """
    Split data for federated learning clients.
    
    Args:
        X: Feature array
        y: Label array
        n_clients: Number of clients
        random_state: Random seed for reproducibility
    
    Returns:
        List of tuples (X_client, y_client) for each client
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n_samples = len(X)
    indices = np.random.permutation(n_samples)
    split_indices = np.array_split(indices, n_clients)
    
    client_data = []
    for idx in split_indices:
        client_data.append((X[idx], y[idx]))
    
    return client_data
