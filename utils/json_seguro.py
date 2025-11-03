import datetime, decimal

def json_seguro(value):
    if isinstance(value, (datetime.date, datetime.datetime)):
        return value.strftime("%d-%m-%Y")
    elif isinstance(value, decimal.Decimal):
        return float(value)
    elif isinstance(value, dict):
        return {k: json_seguro(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [json_seguro(v) for v in value]
    return value
