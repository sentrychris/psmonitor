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
import keyring
import jwt

# Local application imports
import core.database as db
import core.config as cfg


def query_user(username: str) -> dict[str, str] | None:
    """
    Query the database for a given user.
    """

    cursor = db.get_connection()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row  = cursor.fetchone()
    db.close_connection(cursor)

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
        "exp": int((now + timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "type": "access"
    }, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

    return {
        "token": token,
        "user_id": user_id,
    }


def get_credentials() -> tuple[str, str]:
    """
    Get stored credentials from the system keyring.
    """

    username = cfg.get_service_name()
    password = keyring.get_password(cfg.get_service_name("Auth"), username)

    if password is None:
        raise RuntimeError("No stored credentials found. First-run setup may have failed.")

    return username, password
