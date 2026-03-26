# test_connection.py
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("🔍 Testing database connection...")

try:
    from config.database import test_connection
    
    print("📡 Calling test_connection()...")
    result = test_connection()
    
    if result:
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure config/database.py exists")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()