import textwrap
from datetime import timedelta, datetime

from pydantic.v1.generics import check_parameters_count

from .models import SpreadInfo
from .telegram import TelegramAPI

class TelegramNotifier:
    def __init__(self, api_key: str, chat_id):
        self.api_key = api_key
        self.api = TelegramAPI(api_key)
        self.chat_id = chat_id
        self.text_template = textwrap.dedent(
            """
            SPREAD SYMBOL: {symbol},
            SPREAD: {spread}
            {exchange1} -> {exchange2}
            """
        )
        self.symbol_pause = {}
        self.timeout = timedelta(seconds=3)

    def check_pause(self, symbol):
        if symbol in self.symbol_pause:
            if datetime.now() > self.symbol_pause[symbol] + self.timeout:
                del self.symbol_pause[symbol]
                return False
            else:
                return True

        return False

    async def notify(self, spread: SpreadInfo):
        if self.check_pause(spread.symbol):
            return

        kwargs = spread.model_dump(include={'symbol','spread','exchange1','exchange2'})
        kwargs['spread'] = f'{round(kwargs["spread"] * 100,3)}%'
        text = self.text_template.format(**kwargs)
        await self.api.send_message(self.chat_id, text)
        self.symbol_pause[spread.symbol] = datetime.now()

