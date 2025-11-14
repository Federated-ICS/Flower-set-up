# Flower Federated Learning Demo

A minimal federated learning demonstration using Flower framework with anomaly detection models.

## Overview

This project implements a federated learning setup with:
- **1 Server**: Using FedAvg (Federated Averaging) strategy
- **3 Clients**: Each training on their own data partition
- **2 Anomaly Detectors**:
  - sklearn IsolationForest
  - TensorFlow/Keras LSTM Autoencoder
- **Synthetic Data**: Normal and anomalous samples for testing
- **Comprehensive Metrics**: Accuracy, Precision, Recall, F1 Score
- **Model Persistence**: Save and load trained models

## Project Structure

```
Flower-set-up/
├── src/
│   ├── server/
│   │   └── flower_server.py      # Flower server implementation
│   ├── client/
│   │   └── flower_client.py      # Flower client implementation
│   ├── models/
│   │   ├── isolation_forest_detector.py    # IsolationForest model
│   │   └── lstm_autoencoder_detector.py    # LSTM Autoencoder model
│   └── data/
│       └── data_generation.py    # Synthetic data generation
├── run_server.py                 # Script to run the server
├── run_client.py                 # Script to run clients
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Federated-ICS/Flower-set-up.git
cd Flower-set-up
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Federated Learning System

The federated learning system requires running the server and multiple clients.

#### Step 1: Start the Server

In a terminal, run:
```bash
python run_server.py
```

The server will:
- Listen on `0.0.0.0:8080`
- Run 5 federated learning rounds
- Aggregate model updates from all clients
- Log metrics to `server.log`

#### Step 2: Start the Clients

Open **three separate terminals** and run each client:

**Terminal 1 (Client 0):**
```bash
python run_client.py --client-id 0 --model-type lstm_autoencoder
```

**Terminal 2 (Client 1):**
```bash
python run_client.py --client-id 1 --model-type lstm_autoencoder
```

**Terminal 3 (Client 2):**
```bash
python run_client.py --client-id 2 --model-type lstm_autoencoder
```

For IsolationForest model, use:
```bash
python run_client.py --client-id 0 --model-type isolation_forest
```

### Command Line Options

**Server options** (in `run_server.py`):
- Modify `server_address` and `num_rounds` in the script

**Client options:**
- `--client-id`: Client ID (0, 1, or 2)
- `--model-type`: Model type (`lstm_autoencoder` or `isolation_forest`)
- `--server-address`: Server address (default: `localhost:8080`)

## Data Generation

The system automatically generates synthetic data:
- **Normal samples**: Gaussian distribution
- **Anomalous samples**: Shifted mean and higher variance
- **Total**: 900 normal + 100 anomalous samples
- **Split**: Data is divided equally among 3 clients
- **Train/Test**: 80/20 split per client

## Models

### 1. IsolationForest Detector

Uses sklearn's IsolationForest algorithm:
- Unsupervised anomaly detection
- Based on random forest principle
- Contamination parameter: 0.1 (10% expected anomalies)

### 2. LSTM Autoencoder Detector

Uses TensorFlow/Keras LSTM Autoencoder:
- Learns to reconstruct normal patterns
- Anomalies detected by high reconstruction error
- Architecture: LSTM encoder → latent representation → LSTM decoder
- Threshold: 95th percentile of reconstruction error on normal data

## Metrics and Logging

Both models log:
- **Accuracy**: Overall correctness
- **Precision**: True positives / (True positives + False positives)
- **Recall**: True positives / (True positives + False negatives)
- **F1 Score**: Harmonic mean of precision and recall

Logs are saved to:
- `server.log`: Server activities and aggregated metrics
- `client_0.log`, `client_1.log`, `client_2.log`: Individual client logs

## Model Persistence

Trained models are automatically saved to the `models/` directory:
- IsolationForest: `models/client_<id>_isolation_forest`
- LSTM Autoencoder: `models/client_<id>_lstm_autoencoder`

Models can be loaded later using the `load_model()` method.

## Federated Learning Process

1. **Initialization**: Server starts and waits for clients
2. **Client Connection**: 3 clients connect with their local data
3. **Training Round**:
   - Server sends current model to all clients
   - Each client trains on local data
   - Clients send updates back to server
   - Server aggregates updates using FedAvg
4. **Evaluation**: After each round, clients evaluate on local test data
5. **Repeat**: Process repeats for 5 rounds
6. **Completion**: Final models saved locally

## Example Output

```
2025-11-14 15:20:00 - INFO - Starting Federated Learning Server
2025-11-14 15:20:05 - INFO - Client 0 initialized with 266 training samples
2025-11-14 15:20:06 - INFO - Training metrics: {'accuracy': 0.92, 'precision': 0.85, 'recall': 0.78, 'f1_score': 0.81}
2025-11-14 15:20:10 - INFO - Aggregated metrics: {'accuracy': 0.91, 'precision': 0.83, 'recall': 0.79, 'f1_score': 0.80}
```

## Troubleshooting

1. **Connection Issues**: Ensure server is running before starting clients
2. **Port Already in Use**: Change the port in server address
3. **Memory Issues**: Reduce batch size or model complexity
4. **Import Errors**: Verify all dependencies are installed

## License

This project is for educational and research purposes.