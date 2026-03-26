import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
import pymysql
from pymysql import Error


class GuestModel:
    """Model class for guest database operations"""
    
    def __init__(self, db_connection):
        """
        Initialize the GuestModel
        
        Args:
            db_connection: MySQL database connection object
        """
        self.db = db_connection
        print(f"GuestModel initialized")
    
    def add_guest(self, first_name, last_name, email, phone, address):
        """
        Add a new guest to the database
        
        Returns:
            tuple: (success, message, guest_id)
        """
        try:
            print(f"\n=== Adding new guest ===")
            print(f"Name: {first_name} {last_name}")
            print(f"Email: {email}, Phone: {phone}")
            
            cursor = self.db.cursor()
            
            # Check if email already exists
            check_query = "SELECT guest_id FROM guests WHERE email = %s AND is_deleted = 0"
            cursor.execute(check_query, (email,))
            email_exists = cursor.fetchone()
            if email_exists:
                cursor.close()
                return False, "Email already exists. Please use a different email.", None
            
            # Check if phone already exists
            check_query = "SELECT guest_id FROM guests WHERE phone = %s AND is_deleted = 0"
            cursor.execute(check_query, (phone,))
            phone_exists = cursor.fetchone()
            if phone_exists:
                cursor.close()
                return False, "Phone number already exists. Please use a different phone number.", None
            
            # Insert new guest
            insert_query = """
                INSERT INTO guests (first_name, last_name, email, phone, address, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            current_time = datetime.now()
            
            cursor.execute(insert_query, (
                first_name, last_name, email, phone, address, 
                current_time, current_time
            ))
            
            self.db.commit()
            guest_id = cursor.lastrowid
            cursor.close()
            
            print(f"✓ Guest added successfully with ID: {guest_id}")
            return True, "Guest added successfully!", guest_id
            
        except Error as e:
            self.db.rollback()
            print(f"✗ Database Error: {e}")
            return False, f"Database error: {str(e)}", None
        except Exception as e:
            self.db.rollback()
            print(f"✗ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Unexpected error: {str(e)}", None
    
    def get_all_guests(self):
        """
        Get all active guests from the database
        
        Returns:
            list: List of guest dictionaries
        """
        try:
            print("\n=== Fetching all guests ===")
            
            cursor = self.db.cursor()
            query = """
                SELECT guest_id as id, first_name, last_name, email, phone, address
                FROM guests
                WHERE is_deleted = 0
                ORDER BY guest_id DESC
            """
            cursor.execute(query)
            guests = cursor.fetchall()
            cursor.close()
            
            print(f"Found {len(guests)} guests")
            return guests
            
        except Exception as e:
            print(f"Error fetching guests: {e}")
            return []
    
    def update_guest(self, guest_id, first_name, last_name, email, phone, address):
        """
        Update an existing guest
        
        Returns:
            tuple: (success, message)
        """
        try:
            print(f"\n=== Updating guest ID: {guest_id} ===")
            
            cursor = self.db.cursor()
            
            # Check if email exists for other guests
            check_query = """
                SELECT guest_id FROM guests 
                WHERE email = %s AND guest_id != %s AND is_deleted = 0
            """
            cursor.execute(check_query, (email, guest_id))
            if cursor.fetchone():
                cursor.close()
                return False, "Email already exists. Please use a different email."
            
            # Check if phone exists for other guests
            check_query = """
                SELECT guest_id FROM guests 
                WHERE phone = %s AND guest_id != %s AND is_deleted = 0
            """
            cursor.execute(check_query, (phone, guest_id))
            if cursor.fetchone():
                cursor.close()
                return False, "Phone number already exists. Please use a different phone number."
            
            # Update guest
            update_query = """
                UPDATE guests 
                SET first_name = %s, last_name = %s, email = %s, 
                    phone = %s, address = %s, updated_at = %s
                WHERE guest_id = %s AND is_deleted = 0
            """
            cursor.execute(update_query, (
                first_name, last_name, email, phone, address, 
                datetime.now(), guest_id
            ))
            
            self.db.commit()
            cursor.close()
            
            if cursor.rowcount > 0:
                print(f"✓ Guest updated successfully")
                return True, "Guest updated successfully!"
            else:
                return False, "Guest not found or no changes made."
                
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error: {e}")
            return False, f"Error: {str(e)}"
    
    def delete_guest(self, guest_id):
        """
        Soft delete a guest (mark as deleted)
        
        Returns:
            tuple: (success, message)
        """
        try:
            print(f"\n=== Deleting guest ID: {guest_id} ===")
            
            cursor = self.db.cursor()
            
            # Check if guest has any active reservations
            check_query = """
                SELECT COUNT(*) as count FROM reservations 
                WHERE guest_id = %s AND status IN ('CONFIRMED', 'CHECKED_IN')
            """
            cursor.execute(check_query, (guest_id,))
            result = cursor.fetchone()
            
            if result and result['count'] > 0:
                cursor.close()
                return False, "Cannot delete guest with active reservations. Please check them out or cancel first."
            
            # Soft delete the guest
            delete_query = """
                UPDATE guests 
                SET is_deleted = 1, updated_at = %s
                WHERE guest_id = %s AND is_deleted = 0
            """
            cursor.execute(delete_query, (datetime.now(), guest_id))
            self.db.commit()
            cursor.close()
            
            if cursor.rowcount > 0:
                print(f"✓ Guest deleted successfully")
                return True, "Guest deleted successfully!"
            else:
                return False, "Guest not found or already deleted."
                
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error: {e}")
            return False, f"Error: {str(e)}"
    
    def search_guests(self, search_term):
        """
        Search guests by name, email, or phone
        
        Returns:
            list: List of matching guests
        """
        try:
            cursor = self.db.cursor()
            search_pattern = f"%{search_term}%"
            query = """
                SELECT guest_id as id, first_name, last_name, email, phone, address
                FROM guests
                WHERE is_deleted = 0
                AND (
                    first_name LIKE %s OR 
                    last_name LIKE %s OR 
                    email LIKE %s OR 
                    phone LIKE %s
                )
                ORDER BY guest_id DESC
            """
            cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            guests = cursor.fetchall()
            cursor.close()
            return guests
            
        except Exception as e:
            print(f"Error searching guests: {e}")
            return []