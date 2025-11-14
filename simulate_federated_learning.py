"""
Simulation of federated learning without actual network communication.
This demonstrates the complete flow locally for testing purposes.
"""
import sys
import os
import logging
import numpy as np

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.data_generation import generate_dataset, split_data_for_clients
from models.isolation_forest_detector import IsolationForestDetector
from models.lstm_autoencoder_detector import LSTMAutoencoderDetector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def weighted_average_metrics(client_metrics, client_sizes):
    """Aggregate metrics from clients using weighted average."""
    total_samples = sum(client_sizes)
    agg_metrics = {}
    
    for metric_name in client_metrics[0].keys():
        weighted_sum = sum(metrics[metric_name] * size 
                          for metrics, size in zip(client_metrics, client_sizes))
        agg_metrics[metric_name] = weighted_sum / total_samples
    
    return agg_metrics


def federated_averaging(models):
    """
    Simple FedAvg: Average the parameters from all client models.
    For IsolationForest, we just use the first model (can't really average decision trees).
    For LSTM, we average the weights.
    """
    if isinstance(models[0], LSTMAutoencoderDetector):
        # Get parameters from all models
        all_params = [model.get_parameters() for model in models]
        
        # Average parameters (list of weight arrays)
        avg_params = []
        for layer_idx in range(len(all_params[0])):
            # Average this layer's weights across all clients
            layer_weights = [params[layer_idx] for params in all_params]
            avg_weight = np.mean(layer_weights, axis=0)
            avg_params.append(avg_weight)
        
        # Set averaged parameters to all models
        for model in models:
            model.set_parameters(avg_params)
    else:
        # For IsolationForest, we use ensemble voting (keep all models separate)
        # This is a simplification for demo purposes
        pass
    
    return models


def run_federated_learning_simulation(model_type='lstm_autoencoder', num_rounds=5):
    """
    Simulate federated learning with 3 clients and 1 server.
    
    Args:
        model_type: Type of model ('isolation_forest' or 'lstm_autoencoder')
        num_rounds: Number of federated learning rounds
    """
    logger.info("="*70)
    logger.info(f"FEDERATED LEARNING SIMULATION - {model_type.upper()}")
    logger.info("="*70)
    
    # Generate dataset
    logger.info("Generating synthetic dataset...")
    X, y = generate_dataset(n_normal=900, n_anomalous=100, n_features=10, random_state=42)
    logger.info(f"Dataset: {len(X)} samples, {sum(y==0)} normal, {sum(y==1)} anomalous")
    
    # Split data for 3 clients
    logger.info("Splitting data for 3 clients...")
    client_data = split_data_for_clients(X, y, n_clients=3, random_state=42)
    
    # Prepare train/test splits for each client
    client_datasets = []
    for i, (X_client, y_client) in enumerate(client_data):
        split_idx = int(0.8 * len(X_client))
        X_train, X_test = X_client[:split_idx], X_client[split_idx:]
        y_train, y_test = y_client[:split_idx], y_client[split_idx:]
        client_datasets.append((X_train, y_train, X_test, y_test))
        logger.info(f"Client {i}: {len(X_train)} train, {len(X_test)} test samples")
    
    # Initialize models for each client
    logger.info(f"\nInitializing {model_type} models for 3 clients...")
    client_models = []
    for i in range(3):
        if model_type == 'isolation_forest':
            model = IsolationForestDetector(contamination=0.1, random_state=42)
        else:
            model = LSTMAutoencoderDetector(n_features=10, latent_dim=5, sequence_length=1)
        client_models.append(model)
    
    # Federated learning rounds
    for round_num in range(num_rounds):
        logger.info("\n" + "="*70)
        logger.info(f"ROUND {round_num + 1}/{num_rounds}")
        logger.info("="*70)
        
        # Each client trains on local data
        train_metrics_list = []
        eval_metrics_list = []
        train_sizes = []
        test_sizes = []
        
        for client_id, (model, (X_train, y_train, X_test, y_test)) in enumerate(
            zip(client_models, client_datasets)):
            
            logger.info(f"\n--- Client {client_id} Training ---")
            
            # Train on local data
            if model_type == 'lstm_autoencoder':
                train_metrics = model.train(X_train, y_train, epochs=10, batch_size=32)
            else:
                train_metrics = model.train(X_train, y_train)
            
            train_metrics_list.append(train_metrics)
            train_sizes.append(len(X_train))
            
            logger.info(f"Client {client_id} train metrics: "
                       f"Acc={train_metrics['accuracy']:.3f}, "
                       f"Prec={train_metrics['precision']:.3f}, "
                       f"Rec={train_metrics['recall']:.3f}, "
                       f"F1={train_metrics['f1_score']:.3f}")
            
            # Evaluate on local test data
            eval_metrics = model.evaluate(X_test, y_test)
            eval_metrics_list.append(eval_metrics)
            test_sizes.append(len(X_test))
            
            logger.info(f"Client {client_id} eval metrics: "
                       f"Acc={eval_metrics['accuracy']:.3f}, "
                       f"Prec={eval_metrics['precision']:.3f}, "
                       f"Rec={eval_metrics['recall']:.3f}, "
                       f"F1={eval_metrics['f1_score']:.3f}")
        
        # Server aggregates metrics
        agg_train_metrics = weighted_average_metrics(train_metrics_list, train_sizes)
        agg_eval_metrics = weighted_average_metrics(eval_metrics_list, test_sizes)
        
        logger.info(f"\n--- Server Aggregated Metrics (Round {round_num + 1}) ---")
        logger.info(f"Aggregated train metrics: "
                   f"Acc={agg_train_metrics['accuracy']:.3f}, "
                   f"Prec={agg_train_metrics['precision']:.3f}, "
                   f"Rec={agg_train_metrics['recall']:.3f}, "
                   f"F1={agg_train_metrics['f1_score']:.3f}")
        logger.info(f"Aggregated eval metrics: "
                   f"Acc={agg_eval_metrics['accuracy']:.3f}, "
                   f"Prec={agg_eval_metrics['precision']:.3f}, "
                   f"Rec={agg_eval_metrics['recall']:.3f}, "
                   f"F1={agg_eval_metrics['f1_score']:.3f}")
        
        # Server performs federated averaging (only for LSTM)
        if model_type == 'lstm_autoencoder':
            logger.info("\n--- Server performing FedAvg ---")
            client_models = federated_averaging(client_models)
            logger.info("Model parameters averaged across clients")
    
    # Final evaluation
    logger.info("\n" + "="*70)
    logger.info("FINAL EVALUATION")
    logger.info("="*70)
    
    final_metrics_list = []
    final_sizes = []
    
    for client_id, (model, (X_train, y_train, X_test, y_test)) in enumerate(
        zip(client_models, client_datasets)):
        
        final_metrics = model.evaluate(X_test, y_test)
        final_metrics_list.append(final_metrics)
        final_sizes.append(len(X_test))
        
        logger.info(f"Client {client_id} final metrics: "
                   f"Acc={final_metrics['accuracy']:.3f}, "
                   f"Prec={final_metrics['precision']:.3f}, "
                   f"Rec={final_metrics['recall']:.3f}, "
                   f"F1={final_metrics['f1_score']:.3f}")
    
    final_agg_metrics = weighted_average_metrics(final_metrics_list, final_sizes)
    logger.info(f"\nFinal aggregated metrics: "
               f"Acc={final_agg_metrics['accuracy']:.3f}, "
               f"Prec={final_agg_metrics['precision']:.3f}, "
               f"Rec={final_agg_metrics['recall']:.3f}, "
               f"F1={final_agg_metrics['f1_score']:.3f}")
    
    # Save models
    logger.info("\n--- Saving Models ---")
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    
    for client_id, model in enumerate(client_models):
        model_path = os.path.join(model_dir, f"final_client_{client_id}_{model_type}")
        model.save_model(model_path)
        logger.info(f"Saved Client {client_id} model to {model_path}")
    
    logger.info("\n" + "="*70)
    logger.info("SIMULATION COMPLETE")
    logger.info("="*70)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Simulate federated learning')
    parser.add_argument('--model-type', type=str, 
                       choices=['isolation_forest', 'lstm_autoencoder'],
                       default='lstm_autoencoder',
                       help='Type of anomaly detector model')
    parser.add_argument('--num-rounds', type=int, default=3,
                       help='Number of federated learning rounds')
    
    args = parser.parse_args()
    
    run_federated_learning_simulation(args.model_type, args.num_rounds)
