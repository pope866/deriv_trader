import asyncio
import logging
import os
from colorama import Fore, Style
from InquirerPy import inquirer
from InquirerPy.base import Choice
from dotenv import load_dotenv

class CLI:
    def __init__(self, api_client, trading_logic, data_handler, neural_network):
        self.api_client = api_client
        self.trading_logic = trading_logic
        self.data_handler = data_handler
        self.neural_network = neural_network
        self.logger = logging.getLogger(__name__)
        self.is_running = True

    async def main_menu(self):
        """Displays the main menu and handles user input."""
        while self.is_running:
            try:
                choice = await inquirer.select(
                    message="Elige una opción:",
                    choices=[
                        Choice("start", name="Iniciar Trading Automático"),
                        Choice("stop", name="Detener Trading Automático"),
                        Choice("balance", name="Mostrar Balance"),
                        Choice("indicators", name="Mostrar Indicadores"),
                        Choice("train", name="Entrenar Red Neuronal"),
                        Choice("save", name="Guardar Red Neuronal"),
                        Choice("load", name="Cargar Red Neuronal"),
                        Choice("exit", name="Salir"),
                    ],
                    default="exit",
                ).execute_async()

                await self.handle_choice(choice)

            except Exception as e:
                self.logger.error(f"Error en el menú principal: {e}")
                print(Fore.RED + f"Error inesperado: {e}" + Style.RESET_ALL)

    async def handle_choice(self, choice):
        """Handles the user's choice from the main menu."""
        try:
            if choice == "start":
                await self.start_trading()
            elif choice == "stop":
                await self.stop_trading()
            elif choice == "balance":
                await self.show_balance()
            elif choice == "indicators":
                await self.show_indicators()
            elif choice == "train":
                await self.train_network()
            elif choice == "save":
                await self.save_network()
            elif choice == "load":
                await self.load_network()
            elif choice == "exit":
                await self.exit_program()
        except Exception as e:
            self.logger.error(f"Error al manejar la opción: {choice} - {e}")
            print(Fore.RED + f"Error al ejecutar la opción: {e}" + Style.RESET_ALL)

    async def start_trading(self):
        """Starts the trading logic."""
        print(Fore.GREEN + "Iniciando trading automático..." + Style.RESET_ALL)
        await self.trading_logic.start_trading()

    async def stop_trading(self):
        """Stops the trading logic."""
        print(Fore.YELLOW + "Deteniendo trading automático..." + Style.RESET_ALL)
        await self.trading_logic.stop_trading()

    async def show_balance(self):
        """Displays the current account balance."""
        try:
            balance = await self.api_client.get_balance()
            if balance and 'balance' in balance and 'accounts' in balance['balance']:
                for account in balance['balance']['accounts'].values():
                    print(Fore.CYAN + f"Balance: {account['currency']} {account['balance']}" + Style.RESET_ALL)
            else:
                print(Fore.RED + "No se pudo obtener el balance." + Style.RESET_ALL)
        except Exception as e:
            self.logger.error(f"Error al obtener el balance: {e}")
            print(Fore.RED + f"Error al obtener el balance: {e}" + Style.RESET_ALL)

    async def show_indicators(self):
        """Displays the last calculated technical indicators."""
        candle_df = self.data_handler.get_candle_dataframe()
        if candle_df.empty:
            print(Fore.YELLOW + "No hay datos de velas disponibles." + Style.RESET_ALL)
            return

        candle_df = self.data_handler.calculate_technical_indicators(candle_df.copy())  # Work on a copy

        if 'SMA_20' not in candle_df.columns or 'RSI' not in candle_df.columns:
            print(Fore.YELLOW + "No se pudieron calcular los indicadores." + Style.RESET_ALL)
            return

        last_sma = candle_df['SMA_20'].iloc[-1]
        last_rsi = candle_df['RSI'].iloc[-1]

        print(Fore.MAGENTA + f"Última SMA (20): {last_sma:.2f}" + Style.RESET_ALL)
        print(Fore.MAGENTA + f"Último RSI: {last_rsi:.2f}" + Style.RESET_ALL)

    async def train_network(self):
        """Trains the neural network."""
        print(Fore.BLUE + "Entrenando la red neuronal..." + Style.RESET_ALL)
        #TODO: Implementar la lógica para cargar datos, entrenar la red y guardar el modelo
        print(Fore.BLUE + "Red neuronal entrenada." + Style.RESET_ALL)

    async def save_network(self):
        """Saves the neural network model."""
        print(Fore.BLUE + "Guardando la red neuronal..." + Style.RESET_ALL)
        self.neural_network.save_model()
        print(Fore.BLUE + "Red neuronal guardada." + Style.RESET_ALL)

    async def load_network(self):
        """Loads the neural network model."""
        print(Fore.BLUE + "Cargando la red neuronal..." + Style.RESET_ALL)
        if self.neural_network.load_model():
            print(Fore.BLUE + "Red neuronal cargada." + Style.RESET_ALL)
        else:
            print(Fore.RED + "No se pudo cargar la red neuronal." + Style.RESET_ALL)

    async def exit_program(self):
        """Exits the program gracefully."""
        print(Fore.CYAN + "Saliendo del programa..." + Style.RESET_ALL)
        self.is_running = False
        if self.trading_logic.is_trading:
            await self.trading_logic.stop_trading()
        await self.api_client.close()  # Espera a que se cierre la conexión
        #asyncio.get_event_loop().stop() #NO USAR: Evita que el bucle se detenga abruptamente
async def main():
    #Example Usage
    from utils import setup_logger, load_env_vars
    from api_client import DerivClient
    from data_handler import DataHandler
    from neural_network import NeuralNetwork
    from trading_logic import TradingLogic
    import asyncio

    # Load configuration and initialize logger
    load_dotenv()
    env_vars = load_env_vars()
    logger = setup_logger('cli_test', 'logs/cli_test.log')

    # Initialize Deriv API client
    api_client = DerivClient(api_id=1234, token=env_vars["deriv_token"])  # Replace 1234 with your actual app_id
    await api_client.authenticate()

    # Initialize Data Handler
    data_handler = DataHandler()
       # Load the model
    input_shape = (1, 3) #Shape de ejemplo. A futuro, deberás ajustarlo según tus datos.
    nn = NeuralNetwork(input_shape, logger=logger)
    if not nn.load_model():
      logger.warning("No se pudo cargar el modelo al inicio. Asegúrate de entrenarlo o cargarlo.")

    # Initialize Trading Logic
    trading_logic = TradingLogic(api_client, data_handler, nn, env_vars)

    # Inicializar y ejecutar la interfaz de línea de comandos
    cli = CLI(api_client, trading_logic, data_handler, nn)
    await cli.main_menu()

if __name__ == "__main__":
    asyncio.run(main())