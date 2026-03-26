# test_import.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Testing import...")
try:
    from views.AccountManagement.AccountCreation.AdminLoginView import AdminLoginView
    print("✅ Import successful!")
    print(f"Class: {AdminLoginView}")
except Exception as e:
    print(f"❌ Import failed: {e}")
    
    # Show directory structure
    print("\n📁 Directory structure:")
    views_path = os.path.join('views', 'AccountManagement', 'AccountCreation')
    if os.path.exists(views_path):
        print(f"Found: {views_path}")
        files = os.listdir(views_path)
        print(f"Files: {files}")
    else:
        print(f"Path not found: {views_path}")
        