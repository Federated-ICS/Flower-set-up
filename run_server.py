"""
Main script to run the Flower federated learning server.
"""
import logging
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from server.flower_server import start_server


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('server.log')
        ]
    )


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("="*50)
    logger.info("Starting Federated Learning Server")
    logger.info("="*50)
    
    # Configuration
    server_address = "0.0.0.0:8080"
    num_rounds = 5
    
    logger.info(f"Server address: {server_address}")
    logger.info(f"Number of rounds: {num_rounds}")
    
    # Start the server
    start_server(server_address=server_address, num_rounds=num_rounds)
