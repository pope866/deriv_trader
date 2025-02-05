from deriv_api import DerivAPI
import asyncio
import json
import logging

class DerivClient:
    def __init__(self, api_id, token, endpoint='https://api.deriv.com/ws/'):
        self.api = DerivAPI(endpoint=endpoint, app_id=api_id)
        self.token = token
        self.logger = logging.getLogger(__name__)

    async def authenticate(self):
        """Authenticates with the Deriv API."""
        try:
            self.logger.debug("Authenticate: Attempting authentication...")
            self.logger.debug(f"Authenticate: Token = {self.token}")  # Log the token
            response = await self.api.authorize({"authorize": self.token})
            self.logger.debug(f"Authenticate: Response = {response}")  # Log the entire response
            self.logger.info("Authenticate: Authentication successful.")
            return response
        except Exception as e:
            self.logger.exception("Authenticate: Authentication failed:")  # Log the exception with traceback
            return None

    async def subscribe_to_ticks(self, symbol):
        """Subscribes to tick data for the given symbol."""
        try:
            request = {
                "ticks": symbol,
                "subscribe": 1
            }
            response = await self.api.ticks(request)
            self.logger.info(f"Subscribed to ticks for {symbol}: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to subscribe to ticks: {e}")
            return None

    async def subscribe_to_candles(self, symbol, interval):
      """Subscribes to candle data for the given symbol and interval."""
      try:
          request = {
              "ticks_history": symbol,
              "style": "candles",
              "granularity": self.get_granularity(interval),
              "subscribe": 1,
              "count": 20  # Number of candles to retrieve initially
          }
          response = await self.api.ticks_history(request)
          self.logger.info(f"Subscribed to candles for {symbol} with interval {interval}: {response}")
          return response
      except Exception as e:
          self.logger.error(f"Failed to subscribe to candles: {e}")
          return None

    def get_granularity(self, interval):
        """Converts interval string (e.g., '5m') to granularity in seconds."""
        value = int(interval[:-1])
        unit = interval[-1]

        if unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 60 * 60
        elif unit == 'd':
            return value * 60 * 60 * 24
        else:
            raise ValueError(f"Invalid interval unit: {unit}")

    async def buy_contract(self, symbol, contract_type, amount, duration):
      """Buys a contract with the specified parameters."""
      try:
          proposal = await self.api.proposal({
              "amount": amount,
              "basis": "stake",
              "contract_type": contract_type.upper(), # Ensure uppercase
              "currency": "USD",
              "duration": int(duration), # Ensure integer
              "duration_unit": "m",      # Assuming minutes
              "symbol": symbol
          })

          buy = await self.api.buy({
              "buy": proposal['proposal']['id'],
              "price": proposal['proposal']['ask_price']
          })

          self.logger.info(f"Contract bought: {buy}")
          return buy
      except Exception as e:
          self.logger.error(f"Failed to buy contract: {e}")
          return None

    async def get_balance(self):
        """Gets the account balance."""
        try:
            response = await self.api.balance({"account": "all", "subscribe": 1})
            self.logger.info(f"Balance: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}")
            return None

    async def close(self):
        """Closes the connection to the API."""
        await self.api.disconnect()
        self.logger.info("API connection closed.")

    async def forget(self, subscription_id):
        """Forgets a subscription."""
        try:
            response = await self.api.forget(subscription_id)
            self.logger.info(f"Subscription {subscription_id} forgotten: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to forget subscription: {e}")
            return None

    async def forget_all(self, types):
        """Forgets all subscriptions of a given type (e.g., 'ticks', 'candles')."""
        try:
            response = await self.api.forget_all(types)
            self.logger.info(f"All {types} subscriptions forgotten: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Failed to forget all {types} subscriptions: {e}")
            return None

async def main():
    # This is an example - replace with your actual token and app_id.
    # NEVER hardcode your token in a real application!
    from utils import load_env_vars, setup_logger
    env_vars = load_env_vars()
    logger = setup_logger('api_client_test', 'logs/api_client_test.log')

    token = env_vars["deriv_token"]
    symbol = env_vars["symbol"]
    candle_interval = env_vars["candle_interval"]
    contract_type = env_vars["contract_type"]
    amount = env_vars["amount"]
    duration = env_vars["duration"]

    client = DerivClient(api_id=1234, token=token)  # Replace 1234 with your actual app_id
    await client.authenticate()
    await client.get_balance()
    await client.subscribe_to_ticks(symbol)
    await client.subscribe_to_candles(symbol, candle_interval)
    await client.buy_contract(symbol, contract_type, amount, duration)
    await asyncio.sleep(10)  # Keep the connection alive for 10 seconds
    await client.forget_all(['ticks','candles'])
    await client.close()

if __name__ == "__main__":
    asyncio.run(main())