"""
Database Connection Manager for MySQL
Handles connection pooling and query execution
"""

import mysql.connector
from mysql.connector import pooling, Error
import os
from typing import Optional, List, Dict, Any, Tuple


class DatabaseConfig:
    """Database configuration settings"""
    
    # MySQL Configuration - Update these with your credentials
    HOST = "localhost"
    PORT = 3306
    DATABASE = "hotel_ms"
    USER = "root"
    PASSWORD = ""  # Update this to your actual password
    
    # Connection pool settings
    POOL_NAME = "hotel_pool"
    POOL_SIZE = 5


class DatabaseConnection:
    """
    Database connection manager with connection pooling
    Usage:
        with DatabaseConnection() as cursor:
            cursor.execute("SELECT * FROM services")
            results = cursor.fetchall()
    """
    
    _pool = None
    
    @classmethod
    def _get_pool(cls):
        """Get or create connection pool"""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(
                    pool_name=DatabaseConfig.POOL_NAME,
                    pool_size=DatabaseConfig.POOL_SIZE,
                    host=DatabaseConfig.HOST,
                    port=DatabaseConfig.PORT,
                    database=DatabaseConfig.DATABASE,
                    user=DatabaseConfig.USER,
                    password=DatabaseConfig.PASSWORD,
                    autocommit=False
                )
                print(f"✅ Connection pool created for {DatabaseConfig.DATABASE}")
            except Error as e:
                print(f"❌ Error creating connection pool: {e}")
                raise
        return cls._pool
    
    def __init__(self):
        """Get connection from pool"""
        self.connection = None
        self.cursor = None
    
    def __enter__(self):
        """Enter context manager - get connection and cursor"""
        try:
            pool = self._get_pool()
            self.connection = pool.get_connection()
            self.cursor = self.connection.cursor(dictionary=True)
            return self.cursor
        except Error as e:
            print(f"❌ Error getting connection: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager - commit/rollback and close"""
        if exc_type is not None:
            # Exception occurred, rollback
            if self.connection:
                self.connection.rollback()
                print("🔄 Transaction rolled back")
        else:
            # No exception, commit
            if self.connection:
                self.connection.commit()
        
        # Close cursor and connection
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class DatabaseQuery:
    """
    Utility class for common database operations
    """
    
    @staticmethod
    def execute_query(query: str, params: tuple = None) -> bool:
        """
        Execute a query (INSERT, UPDATE, DELETE)
        Returns True if successful, False otherwise
        """
        try:
            with DatabaseConnection() as cursor:
                cursor.execute(query, params or ())
                return True
        except Error as e:
            print(f"❌ Query execution error: {e}")
            return False
    
    @staticmethod
    def fetch_one(query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Fetch a single record"""
        try:
            with DatabaseConnection() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchone()
        except Error as e:
            print(f"❌ Fetch one error: {e}")
            return None
    
    @staticmethod
    def fetch_all(query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Fetch all records"""
        try:
            with DatabaseConnection() as cursor:
                cursor.execute(query, params or ())
                return cursor.fetchall()
        except Error as e:
            print(f"❌ Fetch all error: {e}")
            return []
    
    @staticmethod
    def insert_and_get_id(query: str, params: tuple = None) -> Optional[int]:
        """
        Insert a record and return the auto-generated ID
        """
        try:
            with DatabaseConnection() as cursor:
                cursor.execute(query, params or ())
                return cursor.lastrowid
        except Error as e:
            print(f"❌ Insert error: {e}")
            return None


def test_connection() -> bool:
    """
    Test database connection using direct connection (more reliable)
    Returns True if connection successful
    """
    try:
        print(f"🔌 Attempting to connect to {DatabaseConfig.HOST}:{DatabaseConfig.PORT}/{DatabaseConfig.DATABASE} as {DatabaseConfig.USER}")
        
        # Use direct connection instead of pool for testing
        conn = mysql.connector.connect(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            database=DatabaseConfig.DATABASE,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASSWORD,
            connect_timeout=10
        )
        
        # Test the connection with a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("✅ Database connection successful!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the database connection
    print("Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed. Please check your configuration.")