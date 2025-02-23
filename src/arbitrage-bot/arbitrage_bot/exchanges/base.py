import abc
from typing import List


from ..models import TickerData

class BaseExchange(abc.ABC):

    def __init__(self):
        pass

    @abc.abstractmethod
    async def get_ticker_data(self) -> List[TickerData]:
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass
