from functools import wraps
from localisation import default

L = default['handlers']


def handler(func):
    """Decorator function, prints exceptions instead of exiting."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return f'{L['error']}{repr(e)}'
    return wrapper


def async_handler(func):
    """Decorator function, prints exceptions in an asynchronous functions instead of exiting"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            return f"{L['error']}{repr(e)}"

    return wrapper
