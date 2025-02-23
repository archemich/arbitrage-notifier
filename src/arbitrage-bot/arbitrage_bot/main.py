import asyncio
from typing import List

from .exchanges import ALL_EXCHANGES
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
        for exchange1_type in ALL_EXCHANGES:
            for exchange2_type in ALL_EXCHANGES:
                if exchange1_type == exchange2_type:
                    continue
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
                    if (0.1 > abs(spread) > 0.01):
                        price1, price2 = exchange1_symbols[k], exchange2_symbols[k]
                        if spread > 0:
                            exchange1, exchange2 = exchange2, exchange1
                            price1, price2 = price2, price1

                        spread_info=SpreadInfo(
                            symbol=k,
                            diff=abs(diff),
                            spread=abs(spread),
                            exchange1=exchange1.name,
                            exchange2=exchange2.name,
                            exchange1_price=price1,
                            exchange2_price=price2
                        )
                        res = await notifier.notify(spread_info)
                        diffs.append(spread_info)




def main():
    asyncio.run(_main())

if __name__ == '__main__':
    main()