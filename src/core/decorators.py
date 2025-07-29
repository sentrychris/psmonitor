"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: decorators.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
from functools import wraps


def jwt_required(method):
    """
    Tornado handler method decorator that enforces JWT access token validation.

    Assumes the decorated method belongs to a subclass of `BaseHandler` which
    implements the `get_request_user()` method.

    Args:
        method (coroutine): The original asynchronous request handler method.

    Returns:
        coroutine: A wrapped method that validates the JWT before execution.
    """

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        self.current_user = self.get_request_user()
        return await method(self, *args, **kwargs)

    return wrapper
