from dotenv import load_dotenv
import os
from alpaca.trading.client import TradingClient

load_dotenv()

API_KEY = os.getenv("APCA_API_KEY")
API_SECRET = os.getenv("APCA_API_SECRET")

trading_client = TradingClient(API_KEY, API_SECRET)

positions = trading_client.get_all_positions()

for position in positions:
    print(position.symbol, position.current_price)