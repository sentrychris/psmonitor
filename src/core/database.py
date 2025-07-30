"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: database.py
Author: Chris Rowles <christopher.rowles@outlook.com>
Copyright: © 2025 Chris Rowles. All rights reserved.
Version: 1.6.0.1001
License: MIT
--------------------------------------------------------------------------
"""

# Standard libary imports
import os
import secrets
import sqlite3
import uuid
from dataclasses import dataclass
from typing import TYPE_CHECKING

# Third-party imports
import bcrypt
import keyring

# Local application imports
from core.config import DB_PATH, get_service_name, get_launch_mode

# Type checking
if TYPE_CHECKING:
    from core.logging_manager import PSMonitorLogger

@dataclass
class UserDetails:
    id: str
    username: str
    password: str
    hashed_password: str


def create_user_details() -> UserDetails:
    username = get_service_name()
    password = secrets.token_urlsafe(32)
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    return UserDetails(str(uuid.uuid4()), username, password, hashed)


def init_db(logger: 'PSMonitorLogger') -> None:
    """
    Initialize the database on first run
    """

    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # create schema
        cur.execute("""
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create initial user
        user = create_user_details()
        cur.execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (user.id, user.username, user.hashed_password)
        )

        # Store the password in the system keyring
        keyring.set_password(
            get_service_name('Auth'),
            username=user.username,
            password=user.password
        )

        conn.commit()
        conn.close()
        logger.debug("SQLite database has been initialized")
    else:
        logger.debug("SQLite database already exists, skipping initialization")


def get_connection():
    """
    Open database connection.
    """

    conn = sqlite3.connect(DB_PATH)
    return conn.cursor()


def close_connection(conn: sqlite3.Connection):
    """
    Close database connection.
    """

    conn.close()
