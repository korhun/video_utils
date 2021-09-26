import sys
from inspect import getmembers, isclass, isfunction


def is_debug_mode():
    get_trace = getattr(sys, 'gettrace', None)
    return get_trace is not None


def get_methods(cls_):
    methods = getmembers(cls_, isfunction)
    return dict(methods)


def has_method(cls_, name):
    methods = getmembers(cls_, isfunction)
    return name in dict(methods)
