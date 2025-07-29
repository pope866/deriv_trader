import asyncio
import logging
import os
from dotenv import load_dotenv

from src.api_client import DerivClient
from src.data_handler import DataHandler
from src.neural_network import NeuralNetwork
from src.trading_logic import TradingLogic
from src.cli import CLI
from src.utils import setup_logger, load_env_vars

async def main():
    """Main async function to orchestrate the application."""
    # Load environment variables
    load_dotenv()
    
    # Initialize logging
    logger = setup_logger('main', 'logs/main.log', level=logging.INFO)
    logger.info("Application starting...")
    
    try:
        # Load and validate environment variables
        env_vars = load_env_vars()
        required_vars = ["deriv_token", "api_id"]
        for var in required_vars:
            if var not in env_vars:
                raise ValueError(f"Missing required environment variable: {var}")
        
        # Initialize components
        logger.info("Initializing components...")
        
        api_client = None
        try:
            api_client = DerivClient(
                api_id=int(env_vars["api_id"]),
                token=env_vars["deriv_token"]
            )
            logger.info("Deriv API client initialized successfully")
            
            # Authenticate
            logger.info("Authenticating with Deriv API...")
            await api_client.authenticate()
            logger.info("Authentication successful")
            
            # Initialize other components
            data_handler = DataHandler()
            logger.info("Data handler initialized")
            
            # Neural Network setup - adjust input_shape according to your model
            input_shape = (1, 3)  
            nn = NeuralNetwork(input_shape, logger=logger)
            logger.info("Neural network initialized")
            
            # Try to load pre-trained model
            if nn.load_model():
                logger.info("Model loaded successfully")
            else:
                logger.warning("No pre-trained model found")
            
            # Initialize trading logic
            trading_logic = TradingLogic(api_client, data_handler, nn, env_vars)
            logger.info("Trading logic initialized")
            
            # Start CLI interface
            cli = CLI(api_client, trading_logic, data_handler, nn)
            logger.info("Starting CLI interface...")
            await cli.main_menu()
            
        except Exception as e:
            logger.error(f"Error during component initialization: {str(e)}", exc_info=True)
            raise
        
    except ValueError as ve:
        logger.error(f"Configuration error: {str(ve)}")
        print(f"Configuration error: {str(ve)}")
    except Exception as e:
        logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
        print(f"Critical error occurred. Check logs for details.")
    finally:
        logger.info("Shutting down application...")
        if api_client:
            try:
                await api_client.close()
                logger.info("API client closed successfully")
            except Exception as e:
                logger.error(f"Error closing API client: {str(e)}")
        
        logger.info("Application shutdown complete")
        print("Application has been terminated.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")