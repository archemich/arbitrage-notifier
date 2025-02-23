def validate_symbol(value: str):
    if '/' in value:
        raise ValueError('Symbol must not have /')
    if value.isupper() is False:
        raise ValueError('Symbol must be in UPPERCASE.')

    return value