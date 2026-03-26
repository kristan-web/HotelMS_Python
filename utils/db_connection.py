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
from mysql.connector import Error, errorcode
from config.db_config import DB_CONFIG
import sys


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
            print(f"[DB] Attempting to connect to {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
            print(f"[DB] Database: {DB_CONFIG['database']}")
            print(f"[DB] User: {DB_CONFIG['user']}")
            
            # Try to connect with a timeout
            self._connection = mysql.connector.connect(
                **DB_CONFIG,
                connection_timeout=10  # 10 second timeout
            )
            
            if self._connection and self._connection.is_connected():
                print(f"[DB] ✓ Connected to '{DB_CONFIG['database']}' on {DB_CONFIG['host']}:{DB_CONFIG['port']}")
                
                # Get MySQL version to verify connection
                cursor = self._connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                cursor.close()
                print(f"[DB] MySQL Version: {version[0]}")
                
                return True
            else:
                print("[DB] ✗ Connection failed - no connection established")
                return False
                
        except mysql.connector.Error as e:
            print(f"[DB] ✗ MySQL Error: {e}")
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("[DB]   → Wrong username or password in db_config.py")
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print(f"[DB]   → Database '{DB_CONFIG['database']}' does not exist")
                print("[DB]   → Run schema.sql to create it first")
            else:
                print(f"[DB]   → Error code: {e.errno}")
            self._connection = None
            return False
        except Exception as e:
            print(f"[DB] ✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
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
                print("[DB] Reconnecting...")
                self.connect()
        except Exception as e:
            print(f"[DB] Error checking connection: {e}")
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


def test_connection():
    """Test if we can connect to MySQL server."""
    try:
        # Try to connect without database first to check if server is running
        temp_config = DB_CONFIG.copy()
        temp_config.pop('database', None)
        
        print("[DB] Testing MySQL server connection...")
        conn = mysql.connector.connect(
            host=temp_config['host'],
            port=temp_config['port'],
            user=temp_config['user'],
            password=temp_config['password'],
            connection_timeout=5
        )
        conn.close()
        print("[DB] ✓ MySQL server is reachable")
        
        # Now test with database
        print(f"[DB] Testing database '{DB_CONFIG['database']}'...")
        conn = mysql.connector.connect(
            **DB_CONFIG,
            connection_timeout=5
        )
        conn.close()
        print(f"[DB] ✓ Database '{DB_CONFIG['database']}' exists")
        return True
        
    except mysql.connector.Error as e:
        print(f"[DB] ✗ Connection test failed: {e}")
        return False
    except Exception as e:
        print(f"[DB] ✗ Unexpected error: {e}")
        return False