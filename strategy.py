import numpy as np


def moving_average_strategy(candles):
    """
    Decide BUY / SELL / HOLD from completed 1-minute candles (not raw ticks).
    Uses the candle CLOSE prices, same as any normal charting indicator would.
    """

    if len(candles) < 50:
        return "HOLD"

    closes = [c["close"] for c in candles]

    short_average = np.mean(closes[-10:])
    long_average = np.mean(closes[-50:])

    if short_average > long_average:
        return "BUY"

    elif short_average < long_average:
        return "SELL"

    return "HOLD"
