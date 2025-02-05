import logging
import colorama
from colorama import Fore, Back, Style
import os
from dotenv import load_dotenv
import hashlib
import base64

colorama.init()

def setup_logger(name, log_file, level=logging.INFO):
    """Sets up a logger with color output to console and file."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    # Console handler with color
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColorFormatter())

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

class ColorFormatter(logging.Formatter):
    """Formatter that adds color to log messages."""

    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        log_message = super().format(record)
        return color + log_message + Style.RESET_ALL

def load_env_vars():
    load_dotenv()  # Carga las variables desde .env
    return {
        "deriv_token": os.getenv("DERIV_TOKEN"),
        "account_type": os.getenv("ACCOUNT_TYPE"),
        "symbol": os.getenv("SYMBOL"),
        "candle_interval": os.getenv("CANDLE_INTERVAL"),
        "contract_type": os.getenv("CONTRACT_TYPE"),
        "amount": os.getenv("AMOUNT"),
        "duration": os.getenv("DURATION")
    }

def encrypt_token(token, key="my_secret_key"):
    """Encrypts the token using a simple key (for demonstration purposes ONLY)."""
    key = hashlib.sha256(key.encode()).digest()
    token = token.encode()
    cipher = Fernet(key)
    encrypted_token = cipher.encrypt(token)
    return base64.b64encode(encrypted_token).decode()

def decrypt_token(encrypted_token, key="my_secret_key"):
    """Decrypts the token using the same key."""
    key = hashlib.sha256(key.encode()).digest()
    encrypted_token = base64.b64decode(encrypted_token.encode())
    cipher = Fernet(key)
    decrypted_token = cipher.decrypt(encrypted_token).decode()
    return decrypted_token

if __name__ == '__main__':
    # Example usage
    logger = setup_logger('utils_test', 'logs/utils_test.log')
    logger.debug('This is a debug message.')
    logger.info('This is an info message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')
    logger.critical('This is a critical message.')

    #test .env
    env_vars = load_env_vars()
    print(f"Environment Variables: {env_vars}")

    #Test encryption
    from cryptography.fernet import Fernet
    test_token = "my_super_secret_token"
    encrypted = encrypt_token(test_token)
    print(f"Encrypted token: {encrypted}")
    decrypted = decrypt_token(encrypted)
    print(f"Decrypted token: {decrypted}")