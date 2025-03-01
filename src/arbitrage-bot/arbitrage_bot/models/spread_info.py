from typing import Annotated, Self

from pydantic import BaseModel, Field, field_validator, model_validator

from .validators import validate_symbol


class SpreadInfo(BaseModel):
    symbol: str
    diff: float
    spread: Annotated[float, Field(gt=0, le=1)]
    exchange1: str
    exchange2: str
    exchange1_price: float
    exchange2_price: float



    @field_validator('symbol', mode='after')
    @classmethod
    def validate_symbol(cls, value: str):
        return validate_symbol(value)


    @model_validator(mode='after')
    def exchange_price_ordered(self) -> Self:
        if self.exchange1_price >= self.exchange2_price:
            raise ValueError('exchange1_price must be less than exchange2_price')
        return self