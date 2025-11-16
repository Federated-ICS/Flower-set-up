"""
Flower server implementation for federated learning.
"""
import logging
from typing import List, Tuple

import flwr as fl
from flwr.common import Metrics
from flwr.server.strategy import FedAvg

from streaming.fl_events import RoundMetricPublisher

logger = logging.getLogger(__name__)


def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """
    Aggregate metrics from multiple clients using weighted average.
    """
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


class KafkaFedAvg(FedAvg):
    """FedAvg strategy that publishes aggregated metrics to Kafka."""

    def __init__(self, metric_publisher: RoundMetricPublisher, **kwargs):
        super().__init__(**kwargs)
        self.metric_publisher = metric_publisher

    def aggregate_evaluate(self, server_round, results, failures):
        aggregated_loss, aggregated_metrics = super().aggregate_evaluate(server_round, results, failures)
        if aggregated_metrics is not None:
            logger.info("Server round %s aggregated eval metrics %s", server_round, aggregated_metrics)
            self.metric_publisher.publish(
                aggregated_metrics,
                role="server",
                node_id="server",
                round_id=server_round,
            )
        return aggregated_loss, aggregated_metrics

    def aggregate_fit(self, server_round, results, failures):
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)
        if aggregated_metrics:
            logger.info("Server round %s aggregated fit metrics %s", server_round, aggregated_metrics)
            self.metric_publisher.publish(
                aggregated_metrics,
                role="server",
                node_id="server",
                round_id=server_round,
            )
        return aggregated_parameters, aggregated_metrics


def create_strategy(publisher: RoundMetricPublisher):
    """
    Create a FedAvg strategy for the Flower server.
    """
    strategy = KafkaFedAvg(
        metric_publisher=publisher,
        fraction_fit=1.0,
        fraction_evaluate=1.0,
        min_fit_clients=3,
        min_evaluate_clients=3,
        min_available_clients=3,
        evaluate_metrics_aggregation_fn=weighted_average,
        fit_metrics_aggregation_fn=weighted_average,
    )

    logger.info("KafkaFedAvg strategy created with Kafka metric publishing")
    return strategy


def start_server(server_address="0.0.0.0:8080", num_rounds=5):
    """
    Start the Flower server.
    """
    logger.info(f"Starting Flower server at {server_address} for {num_rounds} rounds")

    with RoundMetricPublisher() as publisher:
        strategy = create_strategy(publisher)

        fl.server.start_server(
            server_address=server_address,
            config=fl.server.ServerConfig(num_rounds=num_rounds),
            strategy=strategy,
        )

    logger.info("Server shutdown")
