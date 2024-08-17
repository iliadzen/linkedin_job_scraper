import urllib
from collections.abc import Iterable


def create_query_string(params):
    key_value_pairs = []
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, Iterable) and type(value) is not str:
            value = ','.join(map(str, value))
        value = urllib.parse.quote(str(value))
        key_value_pairs.append(f"{key}={value}")
    return '&'.join(key_value_pairs)