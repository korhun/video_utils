import sys
from inspect import getmembers, isfunction


def is_debug_mode():
    get_trace = getattr(sys, 'gettrace', None)
    return get_trace is not None


def get_methods(cls_):
    methods = getmembers(cls_, isfunction)
    return dict(methods)


def has_method(cls_, name):
    methods = getmembers(cls_, isfunction)
    return name in dict(methods)


def try_parse_int(txt, default_value=None):
    try:
        return int(txt, 10)
    except ValueError:
        return default_value
