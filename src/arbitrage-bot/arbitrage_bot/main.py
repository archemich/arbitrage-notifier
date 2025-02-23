import asyncio
from typing import List
from itertools import product

from .exchanges import ALL_EXCHANGES
from .settings import get_settings
from .models import SpreadInfo
from .telegram_notifier import TelegramNotifier
from .utils import combine_lists


def compare_ticker_data(price1: float, price2: float):
    diff = price1 - price2
    spread = 0
    if diff > 0:
        spread = diff / price1
    elif diff < 0:
        spread = diff / price2
    return diff, spread


async def _main():
    settings = get_settings()
    notifier = TelegramNotifier(settings.tg_api_key, '@criptti_arb_bot')
    while True:
        exchanges_combinations = combine_lists(ALL_EXCHANGES)
        for exchange1_type, exchange2_type in exchanges_combinations:
            assert exchange1_type != exchange2_type

            exchange1 = exchange1_type()
            exchange2 = exchange2_type()
            exchange1_ticker = await exchange1.get_ticker_data()
            exchange2_ticker = await exchange2.get_ticker_data()

            exchange1_symbols = {x.symbol: x.price for x in exchange1_ticker}
            exchange2_symbols = {x.symbol: x.price for x in exchange2_ticker}
            matched_symbols = exchange1_symbols.keys() & exchange2_symbols.keys()
            diffs: List[SpreadInfo] = []
            for k in matched_symbols:
                diff, spread = compare_ticker_data(exchange1_symbols[k], exchange2_symbols[k])
                if (0.2 > abs(spread) > 0.05):
                    price1, price2 = exchange1_symbols[k], exchange2_symbols[k]
                    name1 = exchange1.name
                    name2 = exchange2.name
                    if spread > 0:
                        name1, name2 = name2, name1
                        price1, price2 = price2, price1

                    spread_info=SpreadInfo(
                        symbol=k,
                        diff=abs(diff),
                        spread=abs(spread),
                        exchange1=name1,
                        exchange2=name2,
                        exchange1_price=price1,
                        exchange2_price=price2
                    )
                    try:
                        res = await notifier.notify(spread_info)
                    except Exception as e:
                        print(f'Notificaiton failed. Reason: {str(e)}')
                    diffs.append(spread_info)




def main():

    asyncio.run(_main())

if __name__ == '__main__':
    main()