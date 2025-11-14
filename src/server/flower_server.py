"""
Flower server implementation for federated learning.
"""
import logging
import flwr as fl
from flwr.server.strategy import FedAvg
from typing import Dict, List, Tuple, Optional
from flwr.common import Metrics

logger = logging.getLogger(__name__)


def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """
    Aggregate metrics from multiple clients using weighted average.
    
    Args:
        metrics: List of tuples (num_examples, metrics_dict)
    
    Returns:
        Aggregated metrics dictionary
    """
    # Calculate weighted averages for each metric
    accuracies = [num_examples * m.get("accuracy", 0) for num_examples, m in metrics]
    precisions = [num_examples * m.get("precision", 0) for num_examples, m in metrics]
    recalls = [num_examples * m.get("recall", 0) for num_examples, m in metrics]
    f1_scores = [num_examples * m.get("f1_score", 0) for num_examples, m in metrics]
    
    total_examples = sum([num_examples for num_examples, _ in metrics])
    
    aggregated = {
        "accuracy": sum(accuracies) / total_examples if total_examples > 0 else 0,
        "precision": sum(precisions) / total_examples if total_examples > 0 else 0,
        "recall": sum(recalls) / total_examples if total_examples > 0 else 0,
        "f1_score": sum(f1_scores) / total_examples if total_examples > 0 else 0,
    }
    
    logger.info(f"Aggregated metrics: {aggregated}")
    return aggregated


def create_strategy():
    """
    Create a FedAvg strategy for the Flower server.
    
    Returns:
        FedAvg strategy instance
    """
    strategy = FedAvg(
        fraction_fit=1.0,  # Use all available clients for training
        fraction_evaluate=1.0,  # Use all available clients for evaluation
        min_fit_clients=3,  # Minimum number of clients for training
        min_evaluate_clients=3,  # Minimum number of clients for evaluation
        min_available_clients=3,  # Minimum number of clients that need to be connected
        evaluate_metrics_aggregation_fn=weighted_average,  # Aggregate evaluation metrics
        fit_metrics_aggregation_fn=weighted_average,  # Aggregate training metrics
    )
    
    logger.info("FedAvg strategy created")
    return strategy


def start_server(server_address="0.0.0.0:8080", num_rounds=5):
    """
    Start the Flower server.
    
    Args:
        server_address: Server address in format "host:port"
        num_rounds: Number of federated learning rounds
    """
    logger.info(f"Starting Flower server at {server_address} for {num_rounds} rounds")
    
    # Create strategy
    strategy = create_strategy()
    
    # Start server
    fl.server.start_server(
        server_address=server_address,
        config=fl.server.ServerConfig(num_rounds=num_rounds),
        strategy=strategy,
    )
    
    logger.info("Server shutdown")
