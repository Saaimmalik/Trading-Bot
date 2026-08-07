import asyncio

from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.common.exceptions import APIError


def get_current_position(client, symbol):
    """Ask Alpaca how many shares we already hold (0 if we hold none)."""
    try:
        position = client.get_open_position(symbol)
        return int(float(position.qty))
    except APIError:
        return 0


def place_order(client, symbol, side, qty):
    """Submit a simple market order and return it (order starts as 'pending')."""
    order_side = OrderSide.BUY if side == "BUY" else OrderSide.SELL

    order = MarketOrderRequest(
        symbol=symbol,
        qty=qty,
        side=order_side,
        time_in_force=TimeInForce.DAY
    )

    return client.submit_order(order)


async def wait_for_fill(client, order_id, poll_seconds=1):
    """Poll Alpaca until the order is filled (or cancelled/rejected/expired)."""
    while True:
        order = client.get_order_by_id(order_id)

        if order.status in ("filled", "canceled", "expired", "rejected"):
            return order

        await asyncio.sleep(poll_seconds)
