"""Clock and JSON representation for Vietnamese business DATETIME values."""
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

VN = ZoneInfo("Asia/Ho_Chi_Minh")

def now():
    return datetime.now(VN).replace(tzinfo=None, microsecond=0)

def as_datetime(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if value.tzinfo is not None:
        value = value.astimezone(VN).replace(tzinfo=None)
    return value

def json_value(value):
    if isinstance(value, datetime):
        return as_datetime(value).replace(tzinfo=VN).isoformat(timespec="seconds")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        if value != value.to_integral_value():
            raise ValueError("Unexpected fractional database value")
        return int(value)
    if isinstance(value, dict):
        return {k: json_value(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_value(v) for v in value]
    return value
