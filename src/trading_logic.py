import logging
import asyncio

class TradingLogic:
    def __init__(self, api_client, data_handler, neural_network, config):
        self.api_client = api_client
        self.data_handler = data_handler
        self.neural_network = neural_network
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.is_trading = False

    async def start_trading(self):
        """Starts the trading loop."""
        self.is_trading = True
        self.logger.info("Trading started.")
        while self.is_trading:
            try:
                await self.trading_cycle()
                await asyncio.sleep(60)  # Check every minute (adjust as needed)
            except Exception as e:
                self.logger.error(f"Error in trading loop: {e}")
                break

    async def stop_trading(self):
        """Stops the trading loop."""
        self.is_trading = False
        self.logger.info("Trading stopped.")

    async def trading_cycle(self):
        """Executes one trading cycle: data analysis, prediction, and trade execution."""
        self.logger.info("Executing trading cycle...")

        # 1. Prepare Data:  Get candle data and calculate indicators
        candle_df = self.data_handler.get_candle_dataframe()
        if candle_df.empty or len(candle_df) < 20:
            self.logger.warning("Not enough candle data to make a decision.")
            return

        candle_df = self.data_handler.calculate_technical_indicators(candle_df.copy())  # Work on a copy
        if candle_df.empty:
            self.logger.warning("Could not calculate indicators. Skipping cycle.")
            return

        # 2. Make Prediction:  Use the latest data point to predict
        last_data = candle_df.iloc[[-1]][['close','SMA_20','RSI']].values  # Get the latest row, select features
        prediction = self.neural_network.predict(last_data.reshape((1,1,3)))  # Reshape for single prediction

        if prediction is None:
            self.logger.warning("Prediction failed. Skipping cycle.")
            return

        # 3. Execute Trade:  Buy a contract based on the prediction
        if prediction > 0.6:  # Example threshold
            trade_direction = "rise"
        elif prediction < 0.4:
            trade_direction = "fall"
        else:
            self.logger.info("Neutral prediction.  Skipping trade.")
            return

        self.logger.info(f"Prediction: {prediction:.2f}, Trade Direction: {trade_direction}")
        if trade_direction == "rise" and self.config["contract_type"]=="rise_fall":
            contract_type = "rise"
        elif trade_direction == "fall" and self.config["contract_type"]=="rise_fall":
            contract_type = "fall"
        elif trade_direction == "rise" and self.config["contract_type"]=="up_down":
          contract_type = "up"
        elif trade_direction == "fall" and self.config["contract_type"]=="up_down":
          contract_type = "down"
        else:
            self.logger.warning("Not Allowed Contract Type")
            return

        buy_result = await self.api_client.buy_contract(
            self.config["symbol"],
            contract_type,
            self.config["amount"],
            self.config["duration"]
        )

        if buy_result:
            self.logger.info(f"Trade executed successfully: {buy_result}")
        else:
            self.logger.error("Trade execution failed.")

async def main():
    # Example Usage (replace with your actual initialization)
    from utils import setup_logger, load_env_vars
    from api_client import DerivClient
    from data_handler import DataHandler
    from neural_network import NeuralNetwork
    import asyncio

    # Load configuration and initialize logger
    env_vars = load_env_vars()
    logger = setup_logger('trading_logic_test', 'logs/trading_logic_test.log')

    # Initialize Deriv API client
    api_client = DerivClient(api_id=1234, token=env_vars["deriv_token"])  # Replace 1234 with your actual app_id
    await api_client.authenticate()

    # Initialize Data Handler
    data_handler = DataHandler()

    # Load the model
    input_shape = (1, 3)
    nn = NeuralNetwork(input_shape, logger=logger)
    if not nn.load_model():
      logger.warning("Please train the model for running the trading")
      exit()

    # Initialize Trading Logic
    trading_logic = TradingLogic(api_client, data_handler, nn, env_vars)

    # Start trading for a limited time
    trading_task = asyncio.create_task(trading_logic.start_trading())
    await asyncio.sleep(60)  # Run for 60 seconds
    await trading_logic.stop_trading()

    await api_client.close()

if __name__ == "__main__":
    asyncio.run(main())