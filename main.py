from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, timezone

from alpaca.data.live import StockDataStream
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.data.enums import DataFeed
from alpaca.common.enums import Sort
from alpaca.trading.client import TradingClient

from strategy import moving_average_strategy
from broker import get_current_position, place_order, wait_for_fill
from data import update_candle, load_historical_candles, candles


load_dotenv()


API_KEY = os.getenv("APCA_API_KEY")
API_SECRET = os.getenv("APCA_API_SECRET")

SYMBOL = "SPY"
TARGET_POSITION = 100


trading_client = TradingClient(
    API_KEY,
    API_SECRET,
    paper=True
)


stream = StockDataStream(
    API_KEY,
    API_SECRET
)


# Separate client just for one-off historical data requests (not live
# streaming) - used once at startup to preload candles.
historical_client = StockHistoricalDataClient(
    API_KEY,
    API_SECRET
)


# Bot state - this is the whole "brain" of the position management logic.
current_position = get_current_position(trading_client, SYMBOL)
previous_signal = "HOLD"
current_signal = "HOLD"
order_pending = False


async def handle_trade(data):
    global previous_signal, current_signal, current_position, order_pending

    completed_candle, is_new_candle = update_candle(data.price, data.timestamp)

    # Still inside the current minute - just keep building the candle, don't
    # touch the strategy or place any orders yet.
    if not is_new_candle:
        return

    # A full 1-minute candle just closed - this is the only moment the
    # strategy is allowed to run.
    previous_signal = current_signal
    current_signal = moving_average_strategy(candles)

    print("----")
    print(
        f"Candle closed: O={completed_candle['open']:.2f} "
        f"H={completed_candle['high']:.2f} "
        f"L={completed_candle['low']:.2f} "
        f"C={completed_candle['close']:.2f}"
    )
    print(f"Previous signal: {previous_signal} | Current signal: {current_signal}")
    print(f"Position: {current_position} | Target: {TARGET_POSITION} | Order pending: {order_pending}")

    if order_pending:
        print("An order is already pending -> skipping this candle")
        return

    if current_signal == previous_signal:
        print("Signal unchanged -> no order needed")
        return

    if current_signal == "BUY":
        qty_needed = TARGET_POSITION - current_position

        if qty_needed <= 0:
            print("Already at or above target position -> no order needed")
            return

        order_pending = True
        print(f"Signal changed to BUY -> buying {qty_needed} shares")

        order = place_order(trading_client, SYMBOL, "BUY", qty_needed)
        await wait_for_fill(trading_client, order.id)

        current_position += qty_needed
        order_pending = False
        print(f"Order filled -> position is now {current_position}")

    elif current_signal == "SELL":
        if current_position <= 0:
            print("No position to close -> no order needed")
            return

        order_pending = True
        print(f"Signal changed to SELL -> closing position of {current_position} shares")

        order = place_order(trading_client, SYMBOL, "SELL", current_position)
        await wait_for_fill(trading_client, order.id)

        current_position = 0
        order_pending = False
        print("Order filled -> position closed")

    else:
        print("Signal is HOLD -> no order needed")


# Preload historical candles so the strategy has 200 candles of data right
# away, instead of needing to wait ~200 live minutes for `candles` to fill up.
# `end` is set to 1 minute ago so we never pull back the still-forming
# "current" minute as if it were a completed candle.
historical_request = StockBarsRequest(
    symbol_or_symbols=SYMBOL,
    timeframe=TimeFrame.Minute,
    end=datetime.now(timezone.utc) - timedelta(minutes=1),
    limit=200,
    sort=Sort.DESC,
    feed=DataFeed.IEX  # free/paper accounts only have access to the IEX feed,
                        # not SIP - same feed the live stream already uses
)

historical_bars = historical_client.get_stock_bars(historical_request)[SYMBOL]
historical_bars.reverse()  # Alpaca gives newest-first with sort=DESC; flip to oldest-first

loaded_count = load_historical_candles(historical_bars)
print(f"Loaded {loaded_count} historical candles for {SYMBOL}")


stream.subscribe_trades(
    handle_trade,
    SYMBOL
)


stream.run()
