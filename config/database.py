"""
Database Configuration Module
Handles MySQL database connections
"""

import pymysql
from pymysql import Error
import time

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # XAMPP default password is empty
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
        print(f"✅ Database connected successfully to {DB_CONFIG['database']}")
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
    print("🔌 Attempting to connect to localhost:3306/hotel_ms as root")
    try:
        conn = get_connection()
        if conn:
            # Test query to verify database is accessible
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            print("✅ Database connection test successful!")
            return True
        return False
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def execute_query(query, params=None):
    """
    Execute a query and return results
    For SELECT queries, returns fetched data
    For INSERT/UPDATE/DELETE, returns affected rows count
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
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
    Execute a query and return one row
    """
    conn = get_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
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

# For backward compatibility
def get_db_connection():
    """Alias for get_connection()"""
    return get_connection()

if __name__ == "__main__":
    # Test the connection when script is run directly
    print("Testing database connection...")
    if test_connection():
        print("✅ Database is ready!")
    else:
        print("❌ Database connection failed!")