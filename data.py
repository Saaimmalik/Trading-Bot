MAX_CANDLES = 200

candles = []          # list of completed 1-minute candles (oldest first)
current_candle = None  # the candle currently being built from live ticks


def update_candle(price, timestamp):
    """
    Feed one trade tick (price + timestamp) into the current 1-minute candle.

    Returns (candle, is_new_candle):
      - While ticks are still landing inside the same minute, updates the
        in-progress candle and returns (None, False).
      - The moment a tick arrives in a NEW minute, the previous minute's
        candle is finalized, stored in `candles`, and returned as
        (completed_candle, True).
    """
    global current_candle

    minute = timestamp.replace(second=0, microsecond=0)

    if current_candle is None:
        current_candle = {
            "start": minute,
            "open": price,
            "high": price,
            "low": price,
            "close": price,
        }
        return None, False

    if minute == current_candle["start"]:
        current_candle["high"] = max(current_candle["high"], price)
        current_candle["low"] = min(current_candle["low"], price)
        current_candle["close"] = price
        return None, False

    # Tick belongs to a new minute -> the old candle is done.
    completed_candle = current_candle
    candles.append(completed_candle)

    if len(candles) > MAX_CANDLES:
        candles.pop(0)

    current_candle = {
        "start": minute,
        "open": price,
        "high": price,
        "low": price,
        "close": price,
    }

    return completed_candle, True


def load_historical_candles(bars):
    """
    Seed the `candles` list with historical bars fetched from Alpaca at
    startup, so the strategy has enough data to run immediately instead of
    waiting ~50 minutes for live candles to build up.

    `bars` should already be sorted oldest -> newest (same order live
    candles get appended in). Each `bar` is an Alpaca Bar object with
    .timestamp/.open/.high/.low/.close attributes - we convert it into our
    own plain-dict candle format so the rest of the code doesn't need to
    know or care whether a candle came from history or from live ticks.

    Mutates `candles` in place (clear + append) rather than replacing it
    with a new list, so the `candles` reference already imported in
    main.py/strategy.py keeps pointing at the same list and sees the data.
    """
    candles.clear()

    for bar in bars:
        candles.append({
            "start": bar.timestamp,
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
        })

    if len(candles) > MAX_CANDLES:
        del candles[:-MAX_CANDLES]

    return len(candles)
