"""
Database Connection Manager
============================
Provides a single shared MySQL connection for the entire application.
Uses a singleton pattern so only one connection is opened at startup.

Usage:
    from utils.db_connection import get_connection
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    cursor.close()
"""

import mysql.connector
from mysql.connector import Error
from config.db_config import DB_CONFIG


class DatabaseConnection:
    """Singleton database connection manager."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self) -> bool:
        """Open the database connection. Returns True on success."""
        try:
            self._connection = mysql.connector.connect(**DB_CONFIG)
            if self._connection.is_connected():
                print(f"[DB] Connected to '{DB_CONFIG['database']}' "
                      f"on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
                return True
        except Error as e:
            print(f"[DB] Connection error: {e}")
            self._connection = None
            return False

    def disconnect(self):
        """Close the database connection."""
        if self._connection and self._connection.is_connected():
            self._connection.close()
            print("[DB] Connection closed.")
        self._connection = None

    def get_connection(self):
        """Return the active connection, reconnecting if needed."""
        try:
            if self._connection is None or not self._connection.is_connected():
                self.connect()
        except Error:
            self.connect()
        return self._connection

    def is_connected(self) -> bool:
        """Check whether the database is reachable."""
        return (self._connection is not None and
                self._connection.is_connected())


# ── Module-level singleton ────────────────────────────────────────────────────
_db = DatabaseConnection()


def get_connection():
    """Return the shared MySQL connection (reconnects automatically)."""
    return _db.get_connection()


def connect():
    """Open the initial connection. Call once at application startup."""
    return _db.connect()


def disconnect():
    """Close the connection. Call once at application shutdown."""
    _db.disconnect()