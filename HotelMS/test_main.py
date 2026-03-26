"""
Minimal test to check if imports work
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Step 1: Testing imports...")

try:
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 imported successfully")
except ImportError as e:
    print(f"✗ PyQt6 import error: {e}")
    sys.exit(1)

try:
    from utils.db_connection import connect, get_connection
    print("✓ db_connection imported successfully")
except ImportError as e:
    print(f"✗ db_connection import error: {e}")
    sys.exit(1)

try:
    from config.db_config import DB_CONFIG
    print("✓ db_config imported successfully")
    print(f"  Database: {DB_CONFIG['database']}")
except ImportError as e:
    print(f"✗ db_config import error: {e}")
    sys.exit(1)

print("\nStep 2: Testing database connection...")
try:
    result = connect()
    if result:
        print("✓ Database connected successfully")
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM guests")
            count = cursor.fetchone()[0]
            cursor.close()
            print(f"✓ Found {count} guests in database")
        else:
            print("✗ Could not get connection")
    else:
        print("✗ Database connection failed")
except Exception as e:
    print(f"✗ Error during connection: {e}")
    import traceback
    traceback.print_exc()

print("\nStep 3: Testing Qt application...")
try:
    app = QApplication(sys.argv)
    print("✓ QApplication created")
    print("Test completed successfully!")
except Exception as e:
    print(f"✗ Error creating QApplication: {e}")