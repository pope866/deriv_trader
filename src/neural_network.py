import logging
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.layers import Input
import numpy as np
import pandas as pd
import os

class NeuralNetwork:
    def __init__(self, input_shape, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.model = self.create_model(input_shape)
        self.model_path = "models/my_model.h5"  # Define model path here

    def create_model(self, input_shape):
        """Creates an LSTM model."""
        model = Sequential()
        model.add(Input(shape=input_shape))  # Capa de entrada
        model.add(LSTM(50, activation='relu'))  # Ya no necesitas input_shape
        model.add(Dense(1, activation='sigmoid'))  # Binary classification (rise/fall)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        self.logger.info("Neural network model created.")
        model.summary()
        return model

    def train(self, X_train, y_train, epochs=10, batch_size=32):
        """Trains the neural network."""
        try:
            self.model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=0)  # Suppress training output
            self.logger.info(f"Neural network trained for {epochs} epochs.")
        except Exception as e:
            self.logger.error(f"Error during training: {e}")

    def predict(self, X):
        """Predicts the probability of 'rise' (1) for the given input."""
        try:
            prediction = self.model.predict(X, verbose=0)  # Suppress prediction output
            self.logger.debug(f"Prediction: {prediction[0][0]}")
            return prediction[0][0]  # Return single probability
        except Exception as e:
            self.logger.error(f"Error during prediction: {e}")
            return None

    def save_model(self):
        """Saves the trained model to a file."""
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)  # Ensure directory exists
            self.model.save(self.model_path)
            self.logger.info(f"Neural network model saved to {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error saving model: {e}")

    def load_model(self):
        """Loads the trained model from a file."""
        try:
            self.model = tf.keras.models.load_model(self.model_path)
            self.logger.info(f"Neural network model loaded from {self.model_path}")
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
        return True

def prepare_data(data, lookback=10):
    """Prepares data for LSTM. lookback is the number of previous time steps to use as input variables to predict the next time period."""
    data = np.asarray(data)  # Convert to NumPy array
    X, y = [], []
    for i in range(lookback, len(data)):
        X.append(data[i-lookback:i])
        y.append(data[i])
    return np.array(X), np.array(y)

if __name__ == '__main__':
    # Example Usage
    from utils import setup_logger
    logger = setup_logger('neural_network_test', 'logs/neural_network_test.log')

    # Generate some dummy data for testing
    num_samples = 100
    lookback = 10  # Number of time steps to look back
    input_dim = 1  # Single feature (e.g., closing price)

    # Generate dummy time series data (replace with your actual data)
    data = np.sin(np.linspace(0, 10 * np.pi, num_samples)) + np.random.normal(0, 0.1, num_samples)

    # Prepare the data for the LSTM model
    X, y = prepare_data(data, lookback)
    X = X.reshape((X.shape[0], X.shape[1], input_dim))  # Reshape for LSTM input
    y = y[lookback-1:]

    # Split data into training and testing (80/20 split)
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]

    # Create a NeuralNetwork instance
    input_shape = (X_train.shape[1], X_train.shape[2])
    nn = NeuralNetwork(input_shape, logger=logger)

    # Train the model
    nn.train(X_train, y_train, epochs=2, batch_size=32)

    # Evaluate the model (simple example)
    loss, accuracy = nn.model.evaluate(X_test, y_test, verbose=0)
    logger.info(f"Test Loss: {loss:.4f}")
    logger.info(f"Test Accuracy: {accuracy:.4f}")

    # Make a prediction
    sample = X_test[0].reshape((1, lookback, input_dim))  # Reshape for single prediction
    prediction = nn.predict(sample)
    logger.info(f"Sample Prediction: {prediction:.4f}")

    # Save the model
    nn.save_model()

    # Load the model and make a prediction
    nn_loaded = NeuralNetwork(input_shape, logger=logger)
    if nn_loaded.load_model():
        prediction_loaded = nn_loaded.predict(sample)
        logger.info(f"Loaded Model Prediction: {prediction_loaded:.4f}")