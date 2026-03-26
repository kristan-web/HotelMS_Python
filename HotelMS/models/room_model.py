# models/room_model.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime


class RoomModel:
    """Model class for room database operations"""
    
    def __init__(self, db_connection):
        """
        Initialize the RoomModel
        
        Args:
            db_connection: MySQL database connection object
        """
        self.db = db_connection
        print("RoomModel initialized")
    
    def add_room(self, room_number, room_type, price, capacity, description):
        """
        Add a new room to the database
        
        Returns:
            tuple: (success, message, room_id)
        """
        try:
            print(f"\n=== Adding new room ===")
            print(f"Room Number: {room_number}")
            print(f"Type: {room_type}, Price: {price}, Capacity: {capacity}")
            
            cursor = self.db.cursor()
            
            # Check if room number already exists
            check_query = "SELECT room_id FROM rooms WHERE room_number = %s"
            cursor.execute(check_query, (room_number,))
            if cursor.fetchone():
                cursor.close()
                return False, f"Room number {room_number} already exists.", None
            
            # Insert new room
            insert_query = """
                INSERT INTO rooms (room_number, room_type, price, capacity, status, description, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            current_time = datetime.now()
            cursor.execute(insert_query, (
                room_number, room_type, float(price), int(capacity), 
                'AVAILABLE', description, current_time, current_time
            ))
            
            self.db.commit()
            room_id = cursor.lastrowid
            cursor.close()
            
            print(f"✓ Room added successfully with ID: {room_id}")
            return True, "Room added successfully!", room_id
            
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error adding room: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error: {str(e)}", None
    
    def get_all_rooms(self):
        """
        Get all rooms from the database
        
        Returns:
            list: List of room dictionaries
        """
        try:
            print("\n=== Fetching all rooms ===")
            
            cursor = self.db.cursor()
            query = """
                SELECT room_id as id, room_number, room_type, price, capacity, status, description
                FROM rooms
                ORDER BY room_number
            """
            cursor.execute(query)
            rooms = cursor.fetchall()
            cursor.close()
            
            print(f"Found {len(rooms)} rooms")
            return rooms
            
        except Exception as e:
            print(f"Error fetching rooms: {e}")
            return []
    
    def update_room(self, room_id, room_number, room_type, price, capacity, status, description):
        """
        Update an existing room
        
        Returns:
            tuple: (success, message)
        """
        try:
            print(f"\n=== Updating room ID: {room_id} ===")
            
            cursor = self.db.cursor()
            
            # Check if room number exists for other rooms
            check_query = """
                SELECT room_id FROM rooms 
                WHERE room_number = %s AND room_id != %s
            """
            cursor.execute(check_query, (room_number, room_id))
            if cursor.fetchone():
                cursor.close()
                return False, f"Room number {room_number} already exists."
            
            # Update room
            update_query = """
                UPDATE rooms 
                SET room_number = %s, room_type = %s, price = %s, 
                    capacity = %s, status = %s, description = %s, updated_at = %s
                WHERE room_id = %s
            """
            cursor.execute(update_query, (
                room_number, room_type, float(price), int(capacity),
                status, description, datetime.now(), room_id
            ))
            
            self.db.commit()
            cursor.close()
            
            if cursor.rowcount > 0:
                print(f"✓ Room updated successfully")
                return True, "Room updated successfully!"
            else:
                return False, "Room not found or no changes made."
                
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error: {e}")
            return False, f"Error: {str(e)}"
    
    def delete_room(self, room_id):
        """
        Delete a room (check if it has active reservations first)
        
        Returns:
            tuple: (success, message)
        """
        try:
            print(f"\n=== Deleting room ID: {room_id} ===")
            
            cursor = self.db.cursor()
            
            # Check if room has any active reservations
            check_query = """
                SELECT COUNT(*) as count FROM reservations 
                WHERE room_id = %s AND status IN ('CONFIRMED', 'CHECKED_IN')
            """
            cursor.execute(check_query, (room_id,))
            result = cursor.fetchone()
            
            if result and result['count'] > 0:
                cursor.close()
                return False, "Cannot delete room with active reservations."
            
            # Delete the room
            delete_query = "DELETE FROM rooms WHERE room_id = %s"
            cursor.execute(delete_query, (room_id,))
            self.db.commit()
            cursor.close()
            
            if cursor.rowcount > 0:
                print(f"✓ Room deleted successfully")
                return True, "Room deleted successfully!"
            else:
                return False, "Room not found."
                
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error: {e}")
            return False, f"Error: {str(e)}"
    
    def update_room_status(self, room_id, status):
        """
        Update room status only
        
        Returns:
            tuple: (success, message)
        """
        try:
            print(f"\n=== Updating room {room_id} status to {status} ===")
            
            cursor = self.db.cursor()
            update_query = """
                UPDATE rooms 
                SET status = %s, updated_at = %s
                WHERE room_id = %s
            """
            cursor.execute(update_query, (status, datetime.now(), room_id))
            self.db.commit()
            cursor.close()
            
            if cursor.rowcount > 0:
                return True, "Room status updated successfully!"
            else:
                return False, "Room not found."
                
        except Exception as e:
            self.db.rollback()
            print(f"✗ Error: {e}")
            return False, f"Error: {str(e)}"
    
    def get_available_rooms(self, room_type=None):
        """
        Get available rooms, optionally filtered by type
        
        Returns:
            list: List of available rooms
        """
        try:
            cursor = self.db.cursor()
            if room_type:
                query = """
                    SELECT room_id as id, room_number, room_type, price, capacity, description
                    FROM rooms
                    WHERE status = 'AVAILABLE' AND room_type = %s
                    ORDER BY room_number
                """
                cursor.execute(query, (room_type,))
            else:
                query = """
                    SELECT room_id as id, room_number, room_type, price, capacity, description
                    FROM rooms
                    WHERE status = 'AVAILABLE'
                    ORDER BY room_number
                """
                cursor.execute(query)
            
            rooms = cursor.fetchall()
            cursor.close()
            return rooms
            
        except Exception as e:
            print(f"Error fetching available rooms: {e}")
            return []