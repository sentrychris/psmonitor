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
    JWT auth decorator.
    """

    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        self.user = self.get_user()
        return await method(self, *args, **kwargs)

    return wrapper
