# test_controller_import.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("Testing controller imports...")
print("=" * 50)

# Test AccountController import
print("\n1. Testing AccountController imports...")
try:
    from controllers.AccountController import AccountController, get_account_controller
    print("✅ Successfully imported AccountController and get_account_controller")
    
    # Test creating an instance
    controller = get_account_controller()
    print(f"✅ Got account controller instance: {controller}")
    
    # Test if it's a singleton (same instance)
    controller2 = get_account_controller()
    print(f"✅ Singleton test: Same instance? {controller is controller2}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test MainController import
print("\n2. Testing MainController import...")
try:
    from controllers.MainController import MainController
    print("✅ Successfully imported MainController")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("Import test complete!")