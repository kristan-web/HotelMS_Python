"""
Quick test script to verify database connection
Run this BEFORE launching main.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 50)
print("Testing Database Connection")
print("=" * 50)

# Test 1: Basic connection
print("\n[Test 1] Testing database connection...")
from config.database import test_connection, get_connection

if test_connection():
    print("✅ Database connection successful!")
else:
    print("❌ Database connection failed!")
    print("   Check: MySQL is running, credentials in config/database.py are correct")
    sys.exit(1)

# Test 2: Query tables
print("\n[Test 2] Checking tables...")
conn = get_connection()
if conn:
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print(f"   Found {len(tables)} tables:")
    for table in tables:
        print(f"     - {table[0]}")
    conn.close()

# Test 3: Check required columns
print("\n[Test 3] Checking required columns...")
conn = get_connection()
if conn:
    cursor = conn.cursor()
    required_columns = [
        ('users', 'is_deleted'),
        ('services', 'is_deleted'),
        ('guests', 'is_deleted'),
        ('rooms', 'is_deleted'),
        ('reservations', 'is_deleted'),
    ]
    
    for table, column in required_columns:
        cursor.execute(f"""
            SELECT COUNT(*) as count 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'hotel_ms' 
            AND TABLE_NAME = '{table}' 
            AND COLUMN_NAME = '{column}'
        """)
        result = cursor.fetchone()
        if result[0] > 0:
            print(f"   ✅ {table}.{column} exists")
        else:
            print(f"   ⚠️  {table}.{column} missing - soft delete may not work")
    
    conn.close()

print("\n" + "=" * 50)
print("Database test complete!")
print("=" * 50)