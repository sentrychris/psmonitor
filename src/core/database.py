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

import os
import sys
import sqlite3
import bcrypt


if getattr(sys, 'frozen', False):
    # Running as a bundled PyInstaller executable
    BUNDLE_DIR = getattr(sys, '_MEIPASS')
else:
    # Running in normal Python environment
    BUNDLE_DIR = os.path.abspath(os.path.join(os.getcwd(), 'bin'))

DB_PATH = os.path.join(BUNDLE_DIR, "auth.db")


def init_db():
    """
    Initialize the database on first run
    """

    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        # create schema
        cur.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # Create initial user for GUI
        gui_password = "secret123"
        hashed = bcrypt.hashpw(gui_password.encode(), bcrypt.gensalt())
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", ("psmonitor", hashed)
        )

        conn.commit()
        conn.close()
        print("Database initialized.")
    else:
        print("Database already exists, skipping initialization.")
