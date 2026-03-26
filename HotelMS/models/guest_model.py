# models/guest_model.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime


class GuestModel:
    """Model class for guest database operations"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        print("GuestModel initialized")
    
    def add_guest(self, first_name, last_name, email, phone, address):
        """Add a new guest to the database"""
        try:
            cursor = self.db.cursor()
            
            # Check if email already exists
            cursor.execute("SELECT guest_id FROM guests WHERE email = %s AND is_deleted = 0", (email,))
            if cursor.fetchone():
                cursor.close()
                return False, "Email already exists.", None
            
            # Check if phone already exists
            cursor.execute("SELECT guest_id FROM guests WHERE phone = %s AND is_deleted = 0", (phone,))
            if cursor.fetchone():
                cursor.close()
                return False, "Phone number already exists.", None
            
            # Insert new guest
            insert_query = """
                INSERT INTO guests (first_name, last_name, email, phone, address, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            now = datetime.now()
            cursor.execute(insert_query, (first_name, last_name, email, phone, address, now, now))
            
            self.db.commit()
            guest_id = cursor.lastrowid
            cursor.close()
            
            return True, "Guest added successfully!", guest_id
            
        except Exception as e:
            self.db.rollback()
            return False, f"Error: {str(e)}", None
    
    def get_all_guests(self):
        """Get all active guests"""
        try:
            cursor = self.db.cursor()
            query = """
                SELECT guest_id as id, first_name, last_name, email, phone, address
                FROM guests WHERE is_deleted = 0 ORDER BY guest_id DESC
            """
            cursor.execute(query)
            guests = cursor.fetchall()
            cursor.close()
            return guests
        except Exception as e:
            print(f"Error fetching guests: {e}")
            return []
    
    def update_guest(self, guest_id, first_name, last_name, email, phone, address):
        """Update existing guest"""
        try:
            cursor = self.db.cursor()
            
            # Check email for other guests
            cursor.execute("SELECT guest_id FROM guests WHERE email = %s AND guest_id != %s AND is_deleted = 0", (email, guest_id))
            if cursor.fetchone():
                cursor.close()
                return False, "Email already exists."
            
            # Check phone for other guests
            cursor.execute("SELECT guest_id FROM guests WHERE phone = %s AND guest_id != %s AND is_deleted = 0", (phone, guest_id))
            if cursor.fetchone():
                cursor.close()
                return False, "Phone number already exists."
            
            # Update guest
            update_query = """
                UPDATE guests SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s, updated_at=%s
                WHERE guest_id=%s AND is_deleted=0
            """
            cursor.execute(update_query, (first_name, last_name, email, phone, address, datetime.now(), guest_id))
            self.db.commit()
            cursor.close()
            
            return True, "Guest updated successfully!"
        except Exception as e:
            self.db.rollback()
            return False, f"Error: {str(e)}"
    
    def delete_guest(self, guest_id):
        """Soft delete guest"""
        try:
            cursor = self.db.cursor()
            
            # Check for active reservations
            cursor.execute("SELECT COUNT(*) as count FROM reservations WHERE guest_id=%s AND status IN ('CONFIRMED', 'CHECKED_IN')", (guest_id,))
            result = cursor.fetchone()
            if result and result['count'] > 0:
                cursor.close()
                return False, "Cannot delete guest with active reservations."
            
            # Soft delete
            cursor.execute("UPDATE guests SET is_deleted=1, updated_at=%s WHERE guest_id=%s", (datetime.now(), guest_id))
            self.db.commit()
            cursor.close()
            
            return True, "Guest deleted successfully!"
        except Exception as e:
            self.db.rollback()
            return False, f"Error: {str(e)}"
    
    def search_guests(self, search_term):
        """Search guests"""
        try:
            cursor = self.db.cursor()
            pattern = f"%{search_term}%"
            query = """
                SELECT guest_id as id, first_name, last_name, email, phone, address
                FROM guests WHERE is_deleted=0 AND (
                    first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR phone LIKE %s
                ) ORDER BY guest_id DESC
            """
            cursor.execute(query, (pattern, pattern, pattern, pattern))
            guests = cursor.fetchall()
            cursor.close()
            return guests
        except Exception as e:
            print(f"Error searching: {e}")
            return []