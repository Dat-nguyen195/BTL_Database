"""Strict API input validation; never truncate amounts or accept booleans as integers."""
import re
from datetime import date
from uuid import UUID
from src.errors import InvalidInputError, BadJsonError

MONEY_MAX = 999_999_999_999
PRICE_MAX = 9_999_999_999
INT_MAX = 2_147_483_647

def fields(value, allowed, required=()):
    if not isinstance(value, dict):
        raise InvalidInputError("Dữ liệu phải là object.")
    if set(value) - set(allowed):
        raise InvalidInputError("Có trường không được phép ghi.")
    if set(required) - set(value):
        raise InvalidInputError("Thiếu trường bắt buộc.")
    return value

def integer(value, name, minimum=0, maximum=MONEY_MAX):
    if type(value) is not int or not minimum <= value <= maximum:
        raise InvalidInputError(f"{name} phải là số nguyên trong [{minimum}, {maximum}].")
    return value

def identifier(value, name, maximum=20, nullable=False):
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1," + str(maximum) + "}", value):
        raise InvalidInputError(f"{name} không hợp lệ hoặc quá dài.")
    return value

def choice(value, name, values):
    if not isinstance(value, str) or value not in values:
        raise InvalidInputError(f"{name} không thuộc miền cho phép.")
    return value

def text(value, name, maximum, nullable=False):
    if nullable and value is None:
        return None
    if not isinstance(value, str) or len(value) > maximum:
        raise InvalidInputError(f"{name} phải là chuỗi tối đa {maximum} ký tự.")
    return value

def request_key(value):
    if not isinstance(value, str) or not value.startswith("nap:"):
        raise InvalidInputError("MaYeuCau phải có dạng nap:{UUID}.")
    try:
        parsed = UUID(value[4:])
    except (ValueError, AttributeError):
        raise InvalidInputError("MaYeuCau phải có dạng nap:{UUID}.")
    if str(parsed) != value[4:].lower():
        raise InvalidInputError("UUID phải có định dạng chuẩn.")
    return value

def date_pair(start, end, required=False):
    if start is None and end is None and not required:
        return None, None
    try:
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", start or "") or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", end or ""):
            raise ValueError()
        a, b = date.fromisoformat(start), date.fromisoformat(end)
        if a > b or b == date.max:
            raise ValueError()
    except (ValueError, TypeError):
        raise InvalidInputError("FromDate/ToDate phải đủ cặp YYYY-MM-DD, đúng thứ tự và có ngày kế tiếp.")
    return start, end

def json_body(request):
    if not request.data:
        return {}
    if not request.is_json:
        raise BadJsonError("Content-Type phải là application/json.")
    try:
        body = request.get_json(silent=False)
    except Exception:
        raise BadJsonError()
    if not isinstance(body, dict):
        raise BadJsonError("JSON body phải là object.")
    return body
