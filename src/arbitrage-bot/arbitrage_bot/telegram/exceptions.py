class TelegramAPIError(Exception):
    def __init__(self, text: str, status: int):
        self.status = status
        self.text = text

class TelegramAPIRateError(TelegramAPIError):
    def __init__(self, text: str, status: int = 429,):
        self.status = status
        self.text = text
