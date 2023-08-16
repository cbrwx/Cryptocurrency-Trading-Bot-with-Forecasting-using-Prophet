import pandas as pd
import ccxt
from prophet import Prophet
import time
from IPython.display import clear_output
import plotly.graph_objects as go
import psutil

trading_fee = 0.001  # 0.1% trading fee - Gate.io has 0.2%, binance has 0.1%, adjust as needed.

def convert_interval_to_seconds(interval):
    number, unit = int(interval[:-1]), interval[-1]
    if unit == 'd':
        return number * 60 * 60 * 24
    elif unit == 'h':
        return number * 60 * 60
    elif unit == 'm':
        return number * 60
    else: 
        return number

exchange = ccxt.gateio({
    'apiKey': 'youapikey',
    'secret': 'yourdirytyapisecret',
})

asset = input("Enter asset name: ")
interval = input("Enter data interval (1m,5m,1h,1d):\n")
steps = int(input("Enter how many last steps to take for prediction:\n")) 
sleep_time_secs = convert_interval_to_seconds(interval)

wallet = {"usdt": 100.0, "asset": 0.0}
trade_every_x_steps = 5
step = 0

def buy(wallet, price):
    amount_to_buy = wallet["usdt"] / price  # Calculate how much you can buy
    fee = amount_to_buy * price * trading_fee  # Calculate the trading fee
    wallet["usdt"] -= amount_to_buy * price + fee  # Subtract the price and the fee from your USDT wallet
    wallet["asset"] += amount_to_buy  # Add the bought amount to your asset wallet
    print(f"Bought {amount_to_buy} of the asset for {amount_to_buy * price} USDT. Fee: {fee} USDT")

def sell(wallet, price):
    amount_to_sell = wallet["asset"]  # Decide how much you want to sell
    fee = amount_to_sell * price * trading_fee  # Calculate the trading fee
    wallet["usdt"] += amount_to_sell * price - fee  # Add the price minus the fee to your USDT wallet
    wallet["asset"] -= amount_to_sell  # Deduct the sold amount from your asset wallet
    print(f"Sold {amount_to_sell} of the asset for {amount_to_sell * price} USDT. Fee: {fee} USDT")

while True:
    
    end_timestamp = exchange.milliseconds()
    start_timestamp = end_timestamp - 12 * 60 * 60 * 1000  
    ohlcv_data = exchange.fetch_ohlcv(asset, interval, start_timestamp)

    df = pd.DataFrame(ohlcv_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
    df['Datetime'] = pd.to_datetime(df['Timestamp'], unit='ms')
    df.set_index('Datetime', inplace=True)
    df = df[['Close']]
    
    df.reset_index(inplace=True)
    df.columns=['ds', 'y'] 
    
    df['ds'] = df['ds'].dt.tz_localize(None)

    model = Prophet()
    model.fit(df.iloc[-steps:])

    future = model.make_future_dataframe(periods=30, freq='T')
    forecast = model.predict(future)

    current_time = pd.Timestamp.now()
    time_delta = pd.Timedelta(hours=12)
    starting_time = current_time - time_delta

    df = df[df['ds'] >= starting_time]
    forecast = forecast[forecast['ds'] >= starting_time]

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=df['ds'], y=df['y'], mode='lines', name='Actual', line=dict(width=7)))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Predicted', line=dict(dash='dash')))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'], fill='tonexty', mode='none', name='Upper Conf Interval'))
    fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'], fill='tonexty', mode='none', name='Lower Conf Interval'))
    fig.show()
        
    print("Current price of the asset: ", df['y'].values[-1])
    last_known_point = df['ds'].max()    
    next_step_pred = forecast[forecast['ds'] > last_known_point].iloc[0]
    print("Prediction for the next step: ", next_step_pred['yhat'])    
    print("Prediction for last step: ", forecast['yhat'].values[-1])
    memory_info = psutil.virtual_memory()
    remaining_memory = memory_info.available / (1024 ** 3)
    print(f"Remaining Memory: {remaining_memory:.2f} GB\n") 

    # calculate the trend and current price at each step
    current_price = df['y'].values[-1]
    trend = 0.6 * next_step_pred['yhat'] + 0.4 * forecast['yhat'].values[-1]

    # make a trading decision at every step
    if trend > current_price and wallet["usdt"] > 0:
        buy(wallet, current_price)
    elif trend < current_price and wallet["asset"] > 0:
        sell(wallet, current_price)
    else:
        print("Holding.")

    # Display asset holdings and calculate total capital
    print("Asset holdings: ", wallet["asset"])
    total_capital = wallet["usdt"] + wallet["asset"] * current_price
    print("Total capital in USDT: ", total_capital)
   
    step += 1
    time.sleep(sleep_time_secs)
    clear_output(wait=True)
