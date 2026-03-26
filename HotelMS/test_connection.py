#!/usr/bin/env python
"""
Simple test script to verify database connection
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Testing Database Connection")
print("=" * 60)

# Test importing config
try:
    from config.db_config import DB_CONFIG
    print("✓ db_config.py loaded successfully")
    print(f"  Host: {DB_CONFIG.get('host')}")
    print(f"  Port: {DB_CONFIG.get('port')}")
    print(f"  Database: {DB_CONFIG.get('database')}")
    print(f"  User: {DB_CONFIG.get('user')}")
    print(f"  Password: {'*' * len(DB_CONFIG.get('password', ''))}")
except ImportError as e:
    print(f"✗ Error loading db_config.py: {e}")
    print("  Please make sure config/db_config.py exists")
    sys.exit(1)

# Test MySQL connection
try:
    import mysql.connector
    from mysql.connector import Error
    
    print("\nAttempting to connect to MySQL...")
    connection = mysql.connector.connect(**DB_CONFIG)
    
    if connection.is_connected():
        print("✓ Database connection successful!")
        
        # Get server info
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"  MySQL Version: {version[0]}")
        
        # Check if database exists
        cursor.execute(f"SHOW DATABASES LIKE '{DB_CONFIG['database']}'")
        db_exists = cursor.fetchone()
        if db_exists:
            print(f"  ✓ Database '{DB_CONFIG['database']}' exists")
            
            # Check if guests table exists
            cursor.execute(f"USE {DB_CONFIG['database']}")
            cursor.execute("SHOW TABLES LIKE 'guests'")
            table_exists = cursor.fetchone()
            if table_exists:
                print("  ✓ Guests table exists")
                
                # Count guests
                cursor.execute("SELECT COUNT(*) FROM guests")
                count = cursor.fetchone()[0]
                print(f"  Total guests: {count}")
            else:
                print("  ✗ Guests table does NOT exist!")
                print("  Please run schema.sql to create the tables")
        else:
            print(f"  ✗ Database '{DB_CONFIG['database']}' does NOT exist!")
            print("  Please run schema.sql to create the database")
        
        cursor.close()
        connection.close()
        print("\n✓ All tests passed!")
        
except Error as e:
    print(f"✗ MySQL Error: {e}")
    print("\nPossible solutions:")
    print("1. Make sure MySQL is running")
    print("2. Check your username and password in config/db_config.py")
    print("3. Make sure the database 'hotel_ms' exists")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)