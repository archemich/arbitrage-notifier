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
            Пара: <code>{symbol}</code>
            Спред: <b>{spread}</b>
            Цена на {exchange1}: {exchange1_price}
            Цена на {exchange2}: {exchange2_price}
            {exchange1} -> {exchange2}
            
            Внимание: на биржах могут оказаться разные торговые пары.
            """
        )
        self.symbol_pause = {}
        self.timeout = timedelta(seconds=10)

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

        kwargs = spread.model_dump(include={'symbol','spread','exchange1','exchange2', 'exchange1_price', 'exchange2_price'})
        kwargs['spread'] = f'{round(kwargs["spread"] * 100, 3)}%'
        text = self.text_template.format(**kwargs)
        await self.api.send_message(self.chat_id, text, parse_mode='HTMl')
        self.symbol_pause[spread.symbol] = datetime.now()

