import aiohttp
from typing import Literal

from urllib.parse import urljoin

from .exceptions import TelegramAPIError

class TelegramAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = f'https://api.telegram.org/'

    def _gen_endpoint(self, method):
        return f'/bot{self.api_key}/{method}'

    async def _do(
            self,
            http_method: str,
            tg_method: str,
            params: dict | None = None,
            json: dict | None = None
    ):
        url = urljoin(self.base_url, self._gen_endpoint(tg_method))
        kwargs = {'url': url}
        if params:
            kwargs['params'] = params
        if json:
            kwargs['json'] = json

        async with aiohttp.ClientSession() as session:
            async with session.request(http_method, **kwargs) as res:
                status = res.status
                if 200 <= status < 300:
                    return await res.json()

                raise TelegramAPIError(status, await res.text())

    async def get(self, tg_method: str, params: dict | None = None):
        return await self._do('GET', tg_method, params=params)

    async def post(self, tg_method: str, json: dict | None = None):
        return await self._do('POST', tg_method, json=json)

    async def send_message(
            self,
            chat_id: str,
            message: str,
            message_thread_id: int = None,
            parse_mode: Literal['MarkdownV2', 'Markdown', 'HTML'] | None = None
    ):
        tjson = {
            'chat_id': chat_id,
            'text': message,
            'message_thread_id': message_thread_id,
            'parse_mode': parse_mode
        }
        json = {k: v for k, v in tjson.items() if v is not None}
        return await self.post('sendMessage', json)
