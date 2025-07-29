"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: auth.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard library imports
from datetime import datetime, timedelta, timezone

# Third-party imports
import bcrypt
import jwt

# Local application imports
from core.database import get_connection, close_connection
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM, JWT_SECRET


def query_user(username: str) -> dict[str, str] | None:
    """
    Get user
    """

    db = get_connection()
    db.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row  = db.fetchone()
    close_connection(db)

    if row:
        return {
            "id": row[0],
            "password": row[1] # hashed
        }

    return None


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify the user's given password.
    """

    return bcrypt.checkpw(password.encode(), hashed)


def generate_token(user_id) -> dict[str, str]:
    """
    Generate user access token.
    """

    now = datetime.now(timezone.utc)
    token = jwt.encode({
        "sub": str(user_id),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "type": "access"
    }, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return {
        "token": token
    }
