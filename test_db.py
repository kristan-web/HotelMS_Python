"""
Database Connection Test Script
Run this to diagnose MySQL connection issues
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

print("=" * 50)
print("DATABASE CONNECTION DIAGNOSTIC TOOL")
print("=" * 50)

# Step 1: Check mysql-connector-python installation
print("\n1. Checking mysql-connector-python...")
try:
    import mysql.connector
    print(f"   ✅ mysql-connector-python version: {mysql.connector.__version__}")
except ImportError as e:
    print(f"   ❌ mysql-connector-python not installed: {e}")
    print("   Run: pip install mysql-connector-python")
    sys.exit(1)

# Step 2: Test direct connection without our wrapper
print("\n2. Testing direct MySQL connection...")

from config.database import DatabaseConfig

print(f"   Host: {DatabaseConfig.HOST}")
print(f"   Port: {DatabaseConfig.PORT}")
print(f"   Database: {DatabaseConfig.DATABASE}")
print(f"   User: {DatabaseConfig.USER}")
print(f"   Password: {'*' * len(DatabaseConfig.PASSWORD) if DatabaseConfig.PASSWORD else '(empty)'}")

try:
    # Try direct connection
    conn = mysql.connector.connect(
        host=DatabaseConfig.HOST,
        port=DatabaseConfig.PORT,
        user=DatabaseConfig.USER,
        password=DatabaseConfig.PASSWORD,
        database=DatabaseConfig.DATABASE,
        connection_timeout=10
    )
    print("   ✅ Direct connection successful!")
    conn.close()
except mysql.connector.Error as e:
    print(f"   ❌ Direct connection failed: {e}")
    print("\n   Possible issues:")
    print("   - MySQL server not running")
    print("   - Wrong host/port")
    print("   - Wrong username/password")
    print("   - Database does not exist")
    sys.exit(1)

# Step 3: Test our DatabaseConnection wrapper
print("\n3. Testing DatabaseConnection wrapper...")

from config.database import DatabaseConnection, test_connection

try:
    with DatabaseConnection() as cursor:
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        if result and result.get('test') == 1:
            print("   ✅ DatabaseConnection wrapper works!")
        else:
            print("   ⚠️ DatabaseConnection returned unexpected result")
except Exception as e:
    print(f"   ❌ DatabaseConnection wrapper failed: {e}")
    sys.exit(1)

# Step 4: Check if services table exists
print("\n4. Checking services table...")

try:
    with DatabaseConnection() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = 'services'
        """, (DatabaseConfig.DATABASE,))
        result = cursor.fetchone()
        
        if result and result.get('count', 0) > 0:
            print("   ✅ services table exists")
            
            # Get count of records
            cursor.execute("SELECT COUNT(*) as total FROM services")
            count_result = cursor.fetchone()
            print(f"   📊 Total services in database: {count_result.get('total', 0)}")
            
            # Show sample data
            cursor.execute("SELECT service_id, name, price, duration, status FROM services LIMIT 5")
            samples = cursor.fetchall()
            if samples:
                print("\n   Sample services:")
                for s in samples:
                    print(f"      - ID: {s['service_id']}, Name: {s['name']}, Price: ₱{s['price']}, Duration: {s['duration']} mins, Status: {s['status']}")
        else:
            print("   ❌ services table does NOT exist")
            print("\n   Please create the table using:")
            print("""
            CREATE TABLE services (
                service_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                price DECIMAL(10,2) NOT NULL,
                duration INT NOT NULL,
                status ENUM('Active', 'Inactive', 'Maintenance') DEFAULT 'Active',
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at DATETIME DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """)
except Exception as e:
    print(f"   ❌ Error checking services table: {e}")

# Step 5: Test ServiceModel
print("\n5. Testing ServiceModel...")

try:
    from models.service_model import ServiceModel
    
    services = ServiceModel.get_all_with_details()
    print(f"   ✅ ServiceModel loaded {len(services)} active services")
    
except Exception as e:
    print(f"   ❌ ServiceModel test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("DIAGNOSTIC COMPLETE")
print("=" * 50)