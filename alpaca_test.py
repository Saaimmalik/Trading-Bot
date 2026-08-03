from dotenv import load_dotenv
import os
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce


load_dotenv()

API_KEY = os.getenv("APCA_API_KEY")
API_SECRET = os.getenv("APCA_API_SECRET")

trading_client = TradingClient(API_KEY, API_SECRET)

limit_order_data = LimitOrderRequest(
    symbol="SPY",
    qty=1,
    side=OrderSide.BUY,
    time_in_force=TimeInForce.DAY,
    limit_price=757.00
)

limit_order = trading_client.submit_order(limit_order_data)
print(limit_order)