"""
Database Configuration Module
Handles MySQL database connections with unified query interface
"""

import pymysql
from pymysql import Error
import time
from typing import Optional, List, Dict, Any, Union

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'hotel_ms',
    'port': 3306,
    'connect_timeout': 5,
    'charset': 'utf8mb4',
    'autocommit': False
}


def get_connection():
    """
    Create and return a database connection
    Returns connection object or None if connection fails
    """
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def test_connection():
    """
    Test database connection
    Returns True if connection successful, False otherwise
    """
    try:
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True
        return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def execute_query(query, params=None):
    """
    Execute a query and return results
    For SELECT queries, returns fetched data as list of dicts
    For INSERT/UPDATE/DELETE, returns affected rows count
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params or ())
        
        if query.strip().upper().startswith('SELECT'):
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.rowcount
            
    except Exception as e:
        print(f"❌ Query execution error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def execute_query_with_commit(query, params=None):
    """
    Execute a query with auto-commit
    Returns affected rows count or None if error
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"❌ Query execution error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def get_one(query, params=None):
    """
    Execute a query and return one row as dict
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    except Exception as e:
        print(f"❌ Query execution error: {e}")
        return None
    finally:
        if conn:
            conn.close()


def insert_one(table, data):
    """
    Insert one record into the specified table
    data: dictionary of column:value pairs
    Returns inserted ID or None if failed
    """
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(query, tuple(data.values()))
        conn.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"❌ Insert error: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


# =============================================================
# DatabaseQuery Class — Unified Interface for Models
# =============================================================

class DatabaseQuery:
    """
    Unified database query interface for models.
    Provides static methods for common database operations.
    """
    
    @staticmethod
    def fetch_all(query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        Execute SELECT query and return all rows as list of dicts.
        Returns empty list if no results or error.
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params or ())
            result = cursor.fetchall()
            return result
        except Exception as e:
            print(f"❌ DatabaseQuery.fetch_all error: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def fetch_one(query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """
        Execute SELECT query and return first row as dict.
        Returns None if no results or error.
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor(pymysql.cursors.DictCursor)
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            return result
        except Exception as e:
            print(f"❌ DatabaseQuery.fetch_one error: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> bool:
        """
        Execute UPDATE/DELETE/INSERT query.
        Returns True if at least one row was affected, False otherwise.
        """
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ DatabaseQuery.execute_query error: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def execute_write(query: str, params: tuple = None) -> int:
        """
        Execute UPDATE/DELETE/INSERT query.
        Returns number of affected rows (0 if error or no rows affected).
        """
        conn = get_connection()
        if not conn:
            return 0
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"❌ DatabaseQuery.execute_write error: {e}")
            if conn:
                conn.rollback()
            return 0
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def insert_and_get_id(query: str, params: tuple = None) -> Optional[int]:
        """
        Execute INSERT query and return the last inserted ID.
        Returns None if insertion failed.
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"❌ DatabaseQuery.insert_and_get_id error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def count(query: str, params: tuple = None) -> int:
        """
        Execute COUNT query and return the count.
        Returns 0 if error or no results.
        """
        result = DatabaseQuery.fetch_one(query, params)
        if result:
            # Try to get the count from the first column
            if 'COUNT(*)' in result:
                return result.get('COUNT(*)', 0)
            # Otherwise return first value
            return list(result.values())[0] if result else 0
        return 0


# For backward compatibility with existing code
def get_db_connection():
    """Alias for get_connection()"""
    return get_connection()


if __name__ == "__main__":
    # Test the connection when script is run directly
    print("Testing database connection...")
    if test_connection():
        print("✅ Database is ready!")
        
        # Test DatabaseQuery
        print("\nTesting DatabaseQuery...")
        result = DatabaseQuery.fetch_one("SELECT 1 as test")
        if result:
            print(f"✅ DatabaseQuery.fetch_one: {result}")
        
        count = DatabaseQuery.count("SELECT COUNT(*) as total FROM users")
        print(f"✅ DatabaseQuery.count: {count} users")
    else:
        print("❌ Database connection failed!")