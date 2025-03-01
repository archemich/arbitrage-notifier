import asyncio
from typing import List, Tuple, Literal

from .exchanges import ALL_EXCHANGES
from .settings import get_settings
from .models import SpreadInfo, TickerData
from .telegram_notifier import TelegramNotifier
from .utils import combine_lists


def compare_ticker_data(ticker_data1: TickerData, ticker_data2: TickerData
                        ) -> Tuple[float, float, Literal['first', 'second']] | None:

    diff1 = ticker_data1.bid_price - ticker_data2.ask_price
    diff2 = ticker_data2.bid_price - ticker_data1.ask_price
    spread1 = diff1 / ticker_data1.bid_price
    spread2 = diff2 / ticker_data2.bid_price
    if spread1 == 0 and spread2 == 0 or spread1 < 0 and spread2 < 0:
        return
    elif spread1 >= spread2:
        diff = diff1
        spread = spread1
        buy_at = 'second'

    elif spread2 > spread1:
        diff = diff2
        spread = spread2
        buy_at = 'first'

    return diff, spread, buy_at


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

            exchange1_symbols = {x.symbol: x for x in exchange1_ticker}
            exchange2_symbols = {x.symbol: x for x in exchange2_ticker}
            matched_symbols = exchange1_symbols.keys() & exchange2_symbols.keys()
            diffs: List[SpreadInfo] = []
            for k in matched_symbols:
                compare_res = compare_ticker_data(exchange1_symbols[k], exchange2_symbols[k])
                if compare_res is None:
                    continue
                diff, spread, buy_at = compare_res
                if spread and (0.2 > abs(spread) > 0.05):
                    print(exchange1_symbols[k], exchange2_symbols[k])
                    price1, price2 = exchange1_symbols[k].ask_price, exchange2_symbols[k].bid_price
                    name1 = exchange1.name
                    name2 = exchange2.name
                    if buy_at == 'second':
                        price1, price2 = exchange2_symbols[k].ask_price, exchange1_symbols[k].bid_price
                        name1, name2 = name2, name1

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
                        print(f'Notification failed. Reason: {str(e)}')
                    diffs.append(spread_info)




def main():
    asyncio.run(_main())

if __name__ == '__main__':
    main()