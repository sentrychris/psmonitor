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
import sqlite3
from datetime import datetime, timedelta, timezone

# Third-party imports
import bcrypt
import jwt
import tornado

# Local application imports
from core.database import DB_PATH
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, \
    JWT_ALGORITHM, JWT_SECRET


def get_user(username: str) -> dict|None:
    """
    Get user
    """

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    row  = cur.fetchone()
    conn.close()

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


def generate_tokens(user_id):
    """
    askjdhaslkj
    """
    now = datetime.now(timezone.utc)

    access_payload = {
        "sub": user_id,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "type": "access"
    }

    refresh_payload = {
        "sub": user_id,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "type": "refresh" 
    }

    return {
        "access_token": jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM),
        "refresh_token": jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM),
    }



def refresh_access_token(refresh_token):
    """
    Refresh access token
    """
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload["type"] != "refresh":
            raise ValueError("Invalid token type")

        return generate_tokens(payload["sub"])
    except jwt.ExpiredSignatureError as e:
        raise tornado.web.HTTPError(401, "Refresh token expired") from e
    except jwt.InvalidTokenError:
        raise tornado.web.HTTPError(401, "Invalid refresh token") from e
