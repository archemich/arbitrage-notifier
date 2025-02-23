from pydantic import BaseModel, field_validator

from .validators import validate_symbol


class TickerData(BaseModel):
    symbol: str  # Assert format is <Sym1><Sym2>. e.g. SOLUSDT
    price: float

    @field_validator('symbol', mode='after')
    @classmethod
    def validate_symbol(cls, value: str):
        return validate_symbol(value)