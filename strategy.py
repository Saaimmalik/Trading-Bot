import numpy as np


def moving_average_strategy(prices):

    if len(prices) < 50:
        return "HOLD"


    short_average = np.mean(prices[-10:])
    long_average = np.mean(prices[-50:])


    if short_average > long_average:
        return "BUY"


    elif short_average < long_average:
        return "SELL"


    return "HOLD"