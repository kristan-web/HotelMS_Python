"""
Room Model for Hotel Management System
Handles CRUD operations for rooms
"""

from typing import Optional, List, Dict, Any
from models.base_model import BaseModel
from config.database import DatabaseQuery


class RoomModel(BaseModel):
    """
    Model for room operations
    Table: rooms
    """
    
    table_name = 'rooms'
    primary_key = 'room_id'
    
    # Columns that should be excluded from automatic updates
    exclude_from_update = ['room_id', 'created_at']
    
    # Room type choices
    ROOM_TYPES = ['SINGLE', 'DOUBLE', 'DELUXE', 'SUITE']
    
    # Status choices
    STATUS_CHOICES = ['AVAILABLE', 'OCCUPIED', 'MAINTENANCE']
    
    @classmethod
    def get_all_active(cls) -> List[Dict[str, Any]]:
        """Get all rooms"""
        query = """
            SELECT 
                room_id as id,
                room_number,
                room_type,
                price,
                capacity,
                status,
                description
            FROM rooms 
            ORDER BY room_number
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_available_rooms(cls, check_in: str, check_out: str) -> List[Dict[str, Any]]:
        """
        Get available rooms for given date range
        Returns rooms not booked during the specified period
        """
        query = """
            SELECT 
                r.room_id as id,
                r.room_number,
                r.room_type,
                r.price,
                r.capacity,
                r.status,
                r.description
            FROM rooms r
            WHERE r.status = 'AVAILABLE'
            AND r.room_id NOT IN (
                SELECT DISTINCT room_id 
                FROM reservations 
                WHERE status NOT IN ('CHECKED_OUT', 'CANCELLED')
                AND (
                    (check_in <= %s AND check_out > %s)
                    OR (check_in < %s AND check_out >= %s)
                    OR (check_in >= %s AND check_out <= %s)
                )
            )
            ORDER BY r.price ASC
        """
        return DatabaseQuery.fetch_all(query, (check_out, check_in, check_out, check_in, check_in, check_out))
    
    @classmethod
    def get_by_id(cls, room_id: int) -> Optional[Dict[str, Any]]:
        """Get room by ID"""
        return cls.find(room_id)
    
    @classmethod
    def get_by_room_number(cls, room_number: str) -> Optional[Dict[str, Any]]:
        """Get room by room number"""
        query = """
            SELECT 
                room_id as id,
                room_number,
                room_type,
                price,
                capacity,
                status,
                description
            FROM rooms 
            WHERE room_number = %s
        """
        return DatabaseQuery.fetch_one(query, (room_number,))
    
    @classmethod
    def create_room(cls, data: Dict[str, Any]) -> Optional[int]:
        """Create a new room with validation"""
        required = ['room_number', 'room_type', 'price', 'capacity']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"{field} is required")
        
        # Check if room number already exists
        existing = cls.get_by_room_number(data['room_number'])
        if existing:
            raise ValueError(f"Room number '{data['room_number']}' already exists")
        
        # Validate price
        try:
            price = float(data['price'])
            if price <= 0:
                raise ValueError("Price must be greater than 0")
        except ValueError:
            raise ValueError("Price must be a valid number")
        
        # Validate capacity
        try:
            capacity = int(data['capacity'])
            if capacity <= 0:
                raise ValueError("Capacity must be greater than 0")
        except ValueError:
            raise ValueError("Capacity must be a valid number")
        
        # Validate room type
        if data['room_type'] not in cls.ROOM_TYPES:
            raise ValueError(f"Room type must be one of: {', '.join(cls.ROOM_TYPES)}")
        
        # Prepare data for insert
        insert_data = {
            'room_number': data['room_number'].strip(),
            'room_type': data['room_type'],
            'price': price,
            'capacity': capacity,
            'status': data.get('status', 'AVAILABLE'),
            'description': data.get('description', '')
        }
        
        return cls.create(insert_data)
    
    @classmethod
    def update_room(cls, room_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing room"""
        existing = cls.find(room_id)
        if not existing:
            raise ValueError(f"Room with ID {room_id} not found")
        
        # Check if room number is being changed and already exists
        if 'room_number' in data:
            existing_room = cls.get_by_room_number(data['room_number'])
            if existing_room and existing_room['id'] != room_id:
                raise ValueError(f"Room number '{data['room_number']}' already exists")
        
        # Validate price if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    raise ValueError("Price must be greater than 0")
                data['price'] = price
            except ValueError:
                raise ValueError("Price must be a valid number")
        
        # Validate capacity if provided
        if 'capacity' in data:
            try:
                capacity = int(data['capacity'])
                if capacity <= 0:
                    raise ValueError("Capacity must be greater than 0")
                data['capacity'] = capacity
            except ValueError:
                raise ValueError("Capacity must be a valid number")
        
        # Validate room type if provided
        if 'room_type' in data and data['room_type'] not in cls.ROOM_TYPES:
            raise ValueError(f"Room type must be one of: {', '.join(cls.ROOM_TYPES)}")
        
        # Validate status if provided
        if 'status' in data and data['status'] not in cls.STATUS_CHOICES:
            raise ValueError(f"Status must be one of: {', '.join(cls.STATUS_CHOICES)}")
        
        # Prepare data for update
        update_data = {}
        if 'room_number' in data:
            update_data['room_number'] = data['room_number'].strip()
        if 'room_type' in data:
            update_data['room_type'] = data['room_type']
        if 'price' in data:
            update_data['price'] = data['price']
        if 'capacity' in data:
            update_data['capacity'] = data['capacity']
        if 'status' in data:
            update_data['status'] = data['status']
        if 'description' in data:
            update_data['description'] = data['description']
        
        return cls.update(room_id, update_data)
    
    @classmethod
    @classmethod
    def update_status(cls, room_id: int, status: str) -> bool:
        """Update room status"""
        try:
            if status not in cls.STATUS_CHOICES:
                raise ValueError(f"Status must be one of: {', '.join(cls.STATUS_CHOICES)}")
        
            # Ensure room_id is int
            room_id_int = int(room_id)
        
            # Direct update query to see if it works
            query = "UPDATE rooms SET status = %s WHERE room_id = %s"
            result = DatabaseQuery.execute_write(query, (status, room_id_int))
        
            print(f"🔍 update_status - room_id: {room_id_int}, status: {status}, result: {result}")
        
            return result > 0
        
        except Exception as e:
            print(f"❌ Error in update_status: {e}")
            return False
    
    @classmethod
    def delete_room(cls, room_id: int) -> bool:
        """Delete a room (hard delete - use with caution)"""
        # Check if room has active reservations
        query = """
            SELECT COUNT(*) as count 
            FROM reservations 
            WHERE room_id = %s 
            AND status NOT IN ('CHECKED_OUT', 'CANCELLED')
        """
        result = DatabaseQuery.fetch_one(query, (room_id,))
        if result and result['count'] > 0:
            raise ValueError("Cannot delete room with active reservations")
        
        return cls.hard_delete(room_id)
    
    @classmethod
    def search_rooms(cls, keyword: str) -> List[Dict[str, Any]]:
        """Search rooms by number or type"""
        if not keyword:
            return cls.get_all_active()
        
        query = """
            SELECT 
                room_id as id,
                room_number,
                room_type,
                price,
                capacity,
                status,
                description
            FROM rooms 
            WHERE room_number LIKE %s 
               OR room_type LIKE %s
            ORDER BY room_number
        """
        like_term = f"%{keyword}%"
        return DatabaseQuery.fetch_all(query, (like_term, like_term))
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get room statistics"""
        query = """
            SELECT 
                COUNT(*) as total_rooms,
                SUM(CASE WHEN status = 'AVAILABLE' THEN 1 ELSE 0 END) as available_rooms,
                SUM(CASE WHEN status = 'OCCUPIED' THEN 1 ELSE 0 END) as occupied_rooms,
                SUM(CASE WHEN status = 'MAINTENANCE' THEN 1 ELSE 0 END) as maintenance_rooms,
                SUM(CASE WHEN room_type = 'SINGLE' THEN 1 ELSE 0 END) as single_rooms,
                SUM(CASE WHEN room_type = 'DOUBLE' THEN 1 ELSE 0 END) as double_rooms,
                SUM(CASE WHEN room_type = 'DELUXE' THEN 1 ELSE 0 END) as deluxe_rooms,
                SUM(CASE WHEN room_type = 'SUITE' THEN 1 ELSE 0 END) as suite_rooms
            FROM rooms
        """
        result = DatabaseQuery.fetch_one(query)
        return result or {}
    
    @classmethod
    def get_room_types(cls) -> List[str]:
        """Get list of room types"""
        return cls.ROOM_TYPES.copy()
    
    @classmethod
    def get_statuses(cls) -> List[str]:
        """Get list of statuses"""
        return cls.STATUS_CHOICES.copy()
    
    @staticmethod
    def update_status(room_id: int, new_status: str) -> bool:
        """Updates room status and returns True if no database error occurs"""
        try:
            from config.database import DatabaseQuery
            query = "UPDATE rooms SET status = %s WHERE room_id = %s"
            # We use execute_write here. 
            # It returns the number of rows changed, but we just care if it doesn't crash.
            DatabaseQuery.execute_write(query, (new_status, room_id))
            return True
        except Exception as e:
            print(f"❌ Model Error: Could not update room status: {e}")
            return False