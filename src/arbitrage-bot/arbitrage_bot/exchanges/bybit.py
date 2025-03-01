from urllib.parse import urljoin
from typing import List

import aiohttp

from ..models import TickerData
from .base import BaseExchange


class BybitExchange(BaseExchange):

    async def get_ticker_data(self) -> List[TickerData]:
        base = 'https://api.bybit.com/'
        endpoint = '/v5/market/tickers/'
        url = urljoin(base, endpoint)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    url,
                    params={'category': 'spot'}
            ) as response:
                res = await(response.json())
                return [
                    TickerData(symbol=x['symbol'], ask_price=float(x['ask1Price']), bid_price=float(x['bid1Price']))
                    for x in res['result']['list']
                    if x['ask1Price'] is not '' and x['bid1Price'] is not ''
                ]

    @property
    def name(self):
        return 'Bybit'