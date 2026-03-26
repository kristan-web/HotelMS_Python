# check_table.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from config.database import get_connection

conn = get_connection()
if conn:
    cursor = conn.cursor()
    
    # Check if users table exists
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # If users table exists, show its structure
    if ('users',) in tables:
        print("\nUsers table structure:")
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[0]}: {col[1]}")
    else:
        print("\nUsers table does not exist!")
    
    cursor.close()
    conn.close()