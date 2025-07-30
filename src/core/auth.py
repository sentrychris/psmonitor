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
import json
from datetime import datetime, timedelta, timezone

# Third-party imports
import bcrypt
import keyring
import jwt

# Local application imports
import core.config as cfg


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
        "exp": int((now + timedelta(seconds=cfg.ACCESS_TOKEN_EXPIRE_SECONDS)).timestamp()),
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


def write_credentials_file() -> str | None:
    """
    Write credentials to file.
    """

    try:
        username, password = get_credentials()
        with open(cfg.CREDENTIALS_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "username": username,
                "password": password
            }, f, indent=4)
        
        return cfg.CREDENTIALS_FILE
    except Exception:
        return None