class TelegramAPIError(Exception):
    def __init__(self, status, text):
        self.status = status
        self.text = text
