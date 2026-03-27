"""
Test model functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 50)
print("Testing Models")
print("=" * 50)

# Test ServiceModel
print("\n[Test 1] Testing ServiceModel...")
from models.service_model import ServiceModel

try:
    services = ServiceModel.get_all_active()
    print(f"   ✅ Found {len(services)} active services")
    if services:
        print(f"      First service: {services[0].get('name', 'N/A')}")
    
    count = ServiceModel.count_active_services()
    print(f"   ✅ Active services count: {count}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test GuestModel
print("\n[Test 2] Testing GuestModel...")
from models.guest_model import GuestModel

try:
    guests = GuestModel.get_all_active()
    print(f"   ✅ Found {len(guests)} active guests")
    if guests:
        print(f"      First guest: {guests[0].get('first_name', 'N/A')} {guests[0].get('last_name', '')}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test RoomModel
print("\n[Test 3] Testing RoomModel...")
from models.room_model import RoomModel

try:
    rooms = RoomModel.get_all_active()
    print(f"   ✅ Found {len(rooms)} rooms")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test ReservationModel
print("\n[Test 4] Testing ReservationModel...")
from models.reservation_model import ReservationModel

try:
    stats = ReservationModel.get_stats()
    print(f"   ✅ Stats: {stats}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("Model test complete!")
print("=" * 50)