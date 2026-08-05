from dotenv import load_dotenv
import os

from alpaca.data.live import StockDataStream
from alpaca.trading.client import TradingClient

from strategy import moving_average_strategy
from broker import place_order
from data import prices


load_dotenv()


API_KEY = os.getenv("APCA_API_KEY")
API_SECRET = os.getenv("APCA_API_SECRET")


trading_client = TradingClient(
    API_KEY,
    API_SECRET,
    paper=True
)


stream = StockDataStream(
    API_KEY,
    API_SECRET
)



async def handle_trade(data):

    prices.append(data.price)


    signal = moving_average_strategy(prices)


    print(
        "Price:",
        data.price,
        "Signal:",
        signal
    )


    if signal != "HOLD":

        place_order(
            trading_client,
            "AAPL",
            signal
        )



stream.subscribe_trades(
    handle_trade,
    "AAPL"
)


stream.run()