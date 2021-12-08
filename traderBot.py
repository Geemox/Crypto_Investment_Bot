import requests
import json
import yfinance as yf
import pycron
import time
from datetime import datetime
from pytz import timezone

CONFIG = json.load(open("./config.json")) # Loads the config file
API_KEY, SECRET_KEY, BASE_URL = CONFIG["API_KEY"], CONFIG["SECRET_KEY"], CONFIG["BASE_URL"]  #Sets Python variables with the config file values

def buy_operation(ticker, quantity):
    """
    find documentation here: https://alpaca.markets/docs/api-documentation/api-v2/orders/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkQuickLabscreateacryptocurrencytradingalgorithminpythonpt229096744-2021-01-01
    send a POST request to "/v2/orders" to create a new order
    :param ticker: stock ticker
    :param quantity:  quantity to buy
    :return: confirmation that the order to buy has been opened
    """
    url = BASE_URL + "/v2/orders"
    payload = json.dumps({
        "symbol": ticker,
        "qty": quantity,
        "side": "buy", # buy, sell
        "type": "market", # market, limit, stop, stop_limit, trailing_stop
        "time_in_force": "day"
    })
    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY,
        'Content-Type': 'application/json'
    }
    return requests.request("POST", url, headers=headers, data=payload).json()

def close_position(ticker):
    """
    find documentation here: https://alpaca.markets/docs/api-documentation/api-v2/positions/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkQuickLabscreateacryptocurrencytradingalgorithminpythonpt229096744-2021-01-01
    sends a DELETE request to "/v2/positions/" to liquidate an open position
    :param ticker: stock ticker
    :return: confirmation that the position has been closed
    """
    url = BASE_URL + "/v2/positions/" + ticker

    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY
    }
    return requests.request("DELETE", url, headers=headers).json()

def get_positions():
    """
    find documentation here: https://alpaca.markets/docs/api-documentation/api-v2/positions/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkQuickLabscreateacryptocurrencytradingalgorithminpythonpt229096744-2021-01-01
    sends a GET request to "/v2/positions" and returns the current positions that are open in our account
    :return: the positions that are held in the alpaca trading account
    """
    url = BASE_URL + "/v2/positions"
    headers = {
        'APCA-API-KEY-ID': API_KEY,
        'APCA-API-SECRET-KEY': SECRET_KEY,
    }
    return requests.request("GET", url, headers=headers).json()

def get_moving_averages(ticker):
    """
    calculates the 9 day and 30 days moving average of the specified ticker
    :param ticker: stock ticker
    :return: returns (9 days moving average, 30 days moving average)
    """
    data = yf.download(ticker, period="3mo", interval='1d')  # Download the last 3months worht of data for the ticker
    data['SMA_9'] = data['Close'].rolling(window=9, min_periods=1).mean()   # Compute a 9-day Simple Moving Average with pandas
    data['SMA_30'] = data['Close'].rolling(window=30, min_periods=1).mean()  # Compute a 30-day Simple Moving Average with pandas
    SMA_9 = float(data.tail(1)["SMA_9"])  # Get the latest calculated 9 days Simple Moving Average
    SMA_30 = float(data.tail(1)["SMA_30"]) # Get the latest 30 days Simple Moving Average
    return SMA_9, SMA_30

if __name__ == "__main__":
    print("Starting the trading algorithm")
    while True:
        # 30 9-15 * * 1-5  is the cron expression that represents: "At minute 30 past every hour from 9 through 15 on every day-of-week from Monday through Friday"
        # https://crontab.guru/?utm_medium=Exinfluencer&utm_source=Exinfluencer&utm_content=000026UJ&utm_term=10006555&utm_id=NA-SkillsNetwork-Channel-SkillsNetworkQuickLabscreateacryptocurrencytradingalgorithminpythonpt229096744-2021-01-01#30_9-15_*_*_1-5
        if pycron.is_now('30 9-15 * * 1-5', dt=datetime.now(timezone('EST'))):
            ticker = "SPY" # The stock to buy/sell
            SMA_9, SMA_30 = get_moving_averages(ticker)
            if SMA_9 > SMA_30:
                # We should buy if we don't already own the st
                if ticker not in [i["symbol"] for i in get_positions()]:
                    print("Currently buying", ticker)
                    buy_operation(ticker, 1)
            if SMA_9 < SMA_30:
                # We should liquidate our position if we own it
                if ticker in [i["symbol"] for i in get_positions()]:
                    print("Currently liquidating our", ticker, "position")
                    close_position(ticker)
            time.sleep(60) # Making sure we don't run the logic twice in a minute
        else:
            time.sleep(20)  # Check again in 20 seconds