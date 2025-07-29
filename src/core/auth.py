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
import tornado

# Local application imports
import core.database as db
import core.config as cfg


def query_user(username: str) -> dict[str, str] | None:
    """
    Get user
    """

    cursor = db.get_connection()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row  = cursor.fetchone()
    db.close_connection(cursor)

    if row:
        return {
            "id": row[0],
            "password": row[1]
        }

    return None


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify the user's given password.
    """

    return bcrypt.checkpw(password.encode(), hashed)


def generate_tokens(user_id) -> dict[str, str]:
    """
    Generate user access and refresh tokens.
    """

    now = datetime.now(timezone.utc)

    access_payload = {
        "sub": str(user_id),
        "exp": int((now + timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
        "type": "access"
    }

    refresh_payload = {
        "sub": str(user_id),
        "exp": int((now + timedelta(days=cfg.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()),
        "type": "refresh" 
    }

    access_token = jwt.encode(access_payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, cfg.JWT_SECRET, algorithm=cfg.JWT_ALGORITHM)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


def refresh_access_token(refresh_token) -> dict[str, str]:
    """
    Issue a new access token using the user's refresh token.
    """

    try:
        payload = jwt.decode(refresh_token, cfg.JWT_SECRET, algorithms=[cfg.JWT_ALGORITHM])
        if payload["type"] != "refresh":
            raise ValueError("Invalid token type")

        return generate_tokens(payload["sub"])
    except jwt.ExpiredSignatureError as e:
        raise tornado.web.HTTPError(401, "Refresh token expired") from e
    except jwt.InvalidTokenError:
        raise tornado.web.HTTPError(401, "Invalid refresh token") from e
