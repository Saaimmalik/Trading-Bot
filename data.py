prices = []


async def handle_trade(data):

    price = data.price

    prices.append(price)

    print(price)

    if len(prices) > 100:
        prices.pop(0)