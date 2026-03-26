"""
Simple database test using alternative connection method
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

print("Testing database connection with alternative method...")

try:
    # Try using pymysql instead (more reliable on Windows)
    import pymysql
    print("✓ pymysql imported successfully")
    
    from config.db_config import DB_CONFIG
    
    print(f"Connecting to {DB_CONFIG['host']}:{DB_CONFIG['port']}...")
    
    connection = pymysql.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        port=DB_CONFIG['port'],
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    
    print("✓ Connected successfully!")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) as count FROM guests")
        result = cursor.fetchone()
        print(f"✓ Found {result['count']} guests")
    
    connection.close()
    print("✓ Connection closed")
    
except ImportError:
    print("pymysql not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
    print("Please run this script again")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    