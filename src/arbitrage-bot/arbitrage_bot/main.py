import asyncio
from typing import List

from .exchanges import BybitExchange, MexcExchange
from .settings import get_settings
from .models import SpreadInfo
from .telegram_notifier import TelegramNotifier


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
        bybit = await BybitExchange().get_ticker_data()
        mexc = await MexcExchange().get_ticker_data()

        bybit_symbols = {x.symbol: x.price for x in bybit}
        mexc_symbols = {x.symbol: x.price for x in mexc}
        matched_symbols = bybit_symbols.keys() & mexc_symbols.keys()
        diffs: List[SpreadInfo] = []
        for k in matched_symbols:
            diff, spread = compare_ticker_data(bybit_symbols[k], mexc_symbols[k])
            if (0.1> abs(spread) > 0.01
                    # and diff > 0.7
            ):


                exchange1, exchange2 = 'Bybit', 'Mexc'
                price1, price2 = bybit_symbols[k], mexc_symbols[k]
                if spread < 0:
                    exchange1, exchange2 = exchange2, exchange1
                    price1, price2 = price2, price1

                spread_info=SpreadInfo(
                    symbol=k,
                    diff=abs(diff),
                    spread=abs(spread),
                    exchange1=exchange1,
                    exchange2=exchange2,
                    exchange1_price=price1,
                    exchange2_price=price2
                )
                res = await notifier.notify(spread_info)
                diffs.append(spread_info)




def main():
    asyncio.run(_main())

if __name__ == '__main__':
    main()