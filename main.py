import asyncio
import logging
import os

from src.api_client import DerivClient
from src.data_handler import DataHandler
from src.neural_network import NeuralNetwork
from src.trading_logic import TradingLogic
from src.cli import CLI
from src.utils import setup_logger, load_env_vars
from dotenv import load_dotenv

# xnaRl4zlCAEyhZQ: Start of main function
async def main():
    """Main function to orchestrate the application."""
    # xnaRl4zlCAEyhZQ: Load configuration and initialize logger
    load_dotenv()
    env_vars = load_env_vars()
    logger = setup_logger('main', 'logs/main.log', level=logging.DEBUG)  # Set level to DEBUG

    try:
        # xnaRl4zlCAEyhZQ: Initialize Deriv API client
        logger.debug("Main: Initializing Deriv API client...")
        api_client = DerivClient(api_id=71513, token=env_vars["deriv_token"])  # Replace 1234 with your actual app_id
        logger.debug("Main: Deriv API client initialized.")

        logger.debug("Main: Authenticating...")
        await api_client.authenticate()
        logger.debug("Main: Authentication completed.")

        # xnaRl4zlCAEyhZQ: Initialize Data Handler
        data_handler = DataHandler()

        # xnaRl4zlCAEyhZQ: Initialize Neural Network
        input_shape = (1, 3)  # Shape de ejemplo - ¡IMPORTANTE: AJUSTAR SEGÚN TUS DATOS!
        nn = NeuralNetwork(input_shape, logger=logger)

        # Optionally load the model (if it exists)
        if not nn.load_model():
            logger.warning("No se pudo cargar el modelo al inicio.  Entrenalo o cárgalo desde el menú.")

        # xnaRl4zlCAEyhZQ: Initialize Trading Logic
        trading_logic = TradingLogic(api_client, data_handler, nn, env_vars)

        # xnaRl4zlCAEyhZQ: Initialize and run the CLI
        cli = CLI(api_client, trading_logic, data_handler, nn)
        await cli.main_menu()

    except Exception as e:
        logger.exception(f"Main: Unhandled exception in main:")
        print(f"Error crítico: {e}")  # Imprime en consola también

    finally:
        # xnaRl4zlCAEyhZQ: Cleanup and close connections
        print("Cerrando conexiones...")
        if 'api_client' in locals() and api_client:
            await api_client.close()
        print("¡Aplicación finalizada!")

if __name__ == "__main__":
    asyncio.run(main())