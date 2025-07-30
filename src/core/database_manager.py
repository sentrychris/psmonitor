"""
--------------------------------------------------------------------------
PSMonitor - System and network monitoring utility

File: server_manager.py
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
from core.config import DB_PATH, get_service_name

# Typing (type hints only, no runtime dependency)
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


class PSMonitorDatabaseManager:
    """
    Manages a Tornado HTTP server running in a background thread.
    """

    def __init__(self, logger: 'PSMonitorLogger' = None):
        """
        Initialize the PSMonitorDatabaseManager.

        Args:
            logger (PSMonitorLogger, optional): Logger instance for debug output.
        """

        self._logger = logger
        self._connection = None


    def connect(self):
        """
        Establish a connection to the SQLite database.

        If already connected, this method does nothing.
        """

        if self._connection is None:
            self._connection = sqlite3.connect(DB_PATH)


    def cursor(self):
        """
        Retrieve a cursor object from the active database connection.

        Returns:
            sqlite3.Cursor | None: A cursor object if connected; otherwise None.
        """

        if self._connection:
            return self._connection.cursor()
        
    
    def commit(self):
        """
        Commit the current transaction to the database.

        Does nothing if no active connection exists.
        """

        if self._connection:
            self._connection.commit()


    def close(self):
        """
        Close the active database connection.

        Resets the internal connection state to None.
        """

        if self._connection:
            self._connection.close()
            self._connection = None


    def initialize(self) -> None:
        """
        Initialize the database schema on first run.

        This method creates the users table if the database does not exist,
        inserts an initial user, stores the password securely in the system keyring,
        and logs the operation if a logger is available.
        """

        if os.path.exists(DB_PATH):
            if self._logger:
                self._logger.debug("SQLite database already exists, skipping initialization.")
            return
        
        self.connect()
        cur = self.cursor()

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
        self.store_user(user)

        # Store the password in the system keyring
        keyring.set_password(
            get_service_name('Auth'),
            username=user.username,
            password=user.password
        )

        self.commit()
        self.close()
        if self._logger:
            self._logger.debug("SQLite database has been initialized")


    def get_user(self, username: str):
        """
        Retrieve a user record from the database by username.

        Args:
            username (str): The username to look up.

        Returns:
            tuple[str, str] | None: A tuple of (id, hashed_password) if found; otherwise None.
        """

        cur = self.cursor()

        cur.execute(
            "SELECT id, password FROM users WHERE username = ?", (username,)
        )
        
        return cur.fetchone()


    def store_user(self, user: UserDetails) -> None:
        """
        Insert a new user into the database.

        Args:
            user (UserDetails): A UserDetails dataclass instance containing user data.
        """

        self.cursor().execute(
            "INSERT INTO users (id, username, password) VALUES (?, ?, ?)",
            (user.id, user.username, user.hashed_password)
        )

    
    def flush_users(self) -> None:
        """
        Remove all users from the database.

        This method deletes all records from the `users` table and commits the change.
        """

        self.cursor().execute("DELETE FROM users")
        self.commit()
