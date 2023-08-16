# Simulated Cryptocurrency Trading Bot with Forecasting using Prophet
This simplified Python script implements a basic cryptocurrency trading bot that utilizes the Prophet time series forecasting model to make trading decisions. The bot fetches historical OHLCV (Open, High, Low, Close, Volume) data from a cryptocurrency exchange, performs time series forecasting using Prophet, and executes buy/sell orders based on predicted price trends. The script requires a functional Gate.io API key.

## How It Works

- The script starts by importing necessary libraries and setting the trading fee (defaulted to 0.1%).

- The convert_interval_to_seconds function is defined to convert different time intervals (e.g., '1d', '1h', '5m') to seconds for data retrieval.

- An instance of the cryptocurrency exchange (ccxt.gateio) is created using your API credentials.

- The user is prompted to input the cryptocurrency asset symbol, data interval (e.g., '1m', '5m', '1h', '1d'), and the number of steps for prediction.

- The script enters an infinite loop to continuously fetch historical OHLCV data from the exchange, preprocess the data, perform time series forecasting using Prophet, and execute trading decisions based on the predicted price trends.

- For each step:

  - OHLCV data is fetched and preprocessed.
  - A Prophet model is trained on the most recent data.
  - A forecast is made for the next steps.
  - The actual and predicted prices are plotted using Plotly.
  - Trading decisions are made based on predicted trends:
  - If the predicted trend is positive and USDT balance is available, a buy order is executed.
  - If the predicted trend is negative and asset balance is available, a sell order is executed.
  
- Asset holdings and total capital are displayed after each step.

## Usage

Ensure you have the required dependencies installed.

- Replace the placeholder API key and secret in the exchange = ccxt.gateio({...}) section with your actual credentials.

- Run the script using a Python interpreter.

- Follow the prompts to enter the asset symbol, data interval, and the number of steps for prediction.

- The script will start fetching data, making forecasts, and executing trades based on predicted trends.

- Observe the Plotly chart showing actual and predicted prices, as well as the trading decisions made by the bot.

Note: The trading bot provided is a simplified implementation and does not cover all aspects of a comprehensive trading strategy. Additional features and risk management mechanisms should be added for a complete and reliable trading solution, as this is; but provided as a starting point, cbrwx.
