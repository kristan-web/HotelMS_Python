# test_import_only.py
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 50)
print("Testing Imports")
print("=" * 50)

print("\n[Step 1] Checking config.database...")
try:
    import config.database as db_module
    print("✅ config.database imported")
    
    # List what's available
    print("\n   Available in config.database:")
    for attr in dir(db_module):
        if not attr.startswith('_'):
            print(f"     - {attr}")
    
    # Check if DatabaseQuery exists
    if hasattr(db_module, 'DatabaseQuery'):
        print("\n   ✅ DatabaseQuery FOUND in config.database!")
    else:
        print("\n   ❌ DatabaseQuery NOT FOUND in config.database!")
        
except Exception as e:
    print(f"❌ Failed to import config.database: {e}")

print("\n[Step 2] Trying direct import of DatabaseQuery...")
try:
    from config.database import DatabaseQuery
    print("✅ Success: from config.database import DatabaseQuery")
    print(f"   DatabaseQuery type: {type(DatabaseQuery)}")
except ImportError as e:
    print(f"❌ Failed: {e}")

print("\n[Step 3] Trying to import base_model...")
try:
    from models.base_model import BaseModel
    print("✅ Success: from models.base_model import BaseModel")
except ImportError as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n[Step 4] Trying to import service_model...")
try:
    from models.service_model import ServiceModel
    print("✅ Success: from models.service_model import ServiceModel")
except ImportError as e:
    print(f"❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Import Test Complete")
print("=" * 50)