from urllib.parse import urljoin
from typing import List

import aiohttp

from ..models import TickerData
from .base import BaseExchange

class MexcExchange(BaseExchange):

    async def get_ticker_data(self) -> List[TickerData]:
        base = 'https://api.mexc.com/'
        endpoint = '/api/v3/ticker/24hr'
        url = urljoin(base, endpoint)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                res = await response.json()
                return [
                    TickerData(symbol=x['symbol'], ask_price=float(x['askPrice']), bid_price=float(x['bidPrice']))
                    for x in res
                ]
    @property
    def name(self):
        return 'Mexc'