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
import sys
import sqlite3
import uuid
from typing import TYPE_CHECKING

# Third-party imports
import bcrypt

# Type checking
if TYPE_CHECKING:
    from core.logging_manager import PSMonitorLogger


if getattr(sys, 'frozen', False):
    # Running as a bundled PyInstaller executable
    BUNDLE_DIR = getattr(sys, '_MEIPASS')
else:
    # Running in normal Python environment
    BUNDLE_DIR = os.path.abspath(os.path.join(os.getcwd(), 'bin'))

DB_PATH = os.path.join(BUNDLE_DIR, "auth.db")


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

        # Create initial user for GUI
        gui_user_id = str(uuid.uuid4())
        gui_username = "psmonitor"
        gui_password = "secret123"
        hashed_password = bcrypt.hashpw(gui_password.encode(), bcrypt.gensalt())

        cur.execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (gui_user_id, gui_username, hashed_password)
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
