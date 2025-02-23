from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_api_key: str

@lru_cache()
def get_settings():
    return Settings()
