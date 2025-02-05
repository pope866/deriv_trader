import logging
import pandas as pd

class DataHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.tick_data = []
        self.candle_data = []

    def process_tick(self, tick):
        """Processes and stores tick data."""
        try:
            self.tick_data.append(tick)
            self.logger.debug(f"Processed tick: {tick['tick']['epoch']}, {tick['tick']['quote']}")
        except Exception as e:
            self.logger.error(f"Error processing tick: {e}")

    def process_candle(self, candle):
        """Processes and stores candle data."""
        try:
          candle_info = candle['candles'][0]
          self.candle_data.append(candle_info)
          self.logger.debug(f"Processed candle: {candle_info['epoch']}, Open: {candle_info['open']}, Close: {candle_info['close']}")
        except Exception as e:
            self.logger.error(f"Error processing candle: {e}")

    def get_tick_dataframe(self):
        """Returns tick data as a Pandas DataFrame."""
        if not self.tick_data:
            return pd.DataFrame()
        return pd.DataFrame([tick['tick'] for tick in self.tick_data])

    def get_candle_dataframe(self):
        """Returns candle data as a Pandas DataFrame."""
        if not self.candle_data:
            return pd.DataFrame()
        return pd.DataFrame(self.candle_data)

    def calculate_technical_indicators(self, df):
        """Calculates simple technical indicators (SMA, RSI - example)."""
        try:
            df['SMA_20'] = df['close'].rolling(window=20).mean()
            # Simple RSI (not optimized for performance)
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            df['RSI'] = 100 - (100 / (1 + rs))
            self.logger.info("Technical indicators calculated.")
            return df
        except Exception as e:
            self.logger.error(f"Error calculating technical indicators: {e}")
            return df

if __name__ == '__main__':
    # Example Usage
    from utils import setup_logger
    import numpy as np
    logger = setup_logger('data_handler_test', 'logs/data_handler_test.log')
    handler = DataHandler()

    # Simulate some tick data
    sample_ticks = [{'tick': {'epoch': 1678886400 + i, 'quote': np.random.rand() * 100}} for i in range(5)]
    for tick in sample_ticks:
        handler.process_tick(tick)

    # Simulate some candle data
    sample_candles = [{'candles':[{'epoch': 1678886400 + i, 'open': np.random.rand() * 100,'close': np.random.rand() * 100, 'high': np.random.rand() * 100,'low': np.random.rand() * 100}]} for i in range(5)]
    for candle in sample_candles:
        handler.process_candle(candle)

    tick_df = handler.get_tick_dataframe()
    candle_df = handler.get_candle_dataframe()

    if not tick_df.empty:
        print("Tick Dataframe:")
        print(tick_df)

    if not candle_df.empty:
        print("\nCandle Dataframe:")
        print(candle_df)
        candle_df = handler.calculate_technical_indicators(candle_df)
        print("\nCandle Dataframe with Indicators:")
        print(candle_df)