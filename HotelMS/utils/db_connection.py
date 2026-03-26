# utils/db_connection.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pymysql
from pymysql import Error
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
            print(f"Connecting to MySQL at {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
            self._connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                port=DB_CONFIG['port'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                connect_timeout=10,
                autocommit=False
            )
            print(f"[DB] Connected to '{DB_CONFIG['database']}'")
            return True
        except Error as e:
            print(f"[DB] Connection error: {e}")
            self._connection = None
            return False

    def disconnect(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            print("[DB] Connection closed.")
        self._connection = None

    def get_connection(self):
        """Return the active connection, reconnecting if needed."""
        if self._connection is None:
            self.connect()
        return self._connection


_db = DatabaseConnection()


def get_connection():
    return _db.get_connection()


def connect():
    return _db.connect()


def disconnect():
    _db.disconnect()