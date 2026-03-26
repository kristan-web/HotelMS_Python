"""
Room Controller
================
Manages room operations, connects RoomModel with views.
Handles validation and availability checking.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.room_model import RoomModel


class RoomController:
    """Controller for room management operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── DATA TRANSFORMATION ────────────────────────────────────────────────
    def _transform_room(self, room: dict) -> dict:
        """Convert room_id to id for view compatibility."""
        if not room:
            return None
        return {
            'id': room['room_id'],
            'room_number': room['room_number'],
            'room_type': room['room_type'],
            'price': float(room['price']),
            'capacity': room['capacity'],
            'status': room['status'],
            'description': room.get('description', '')
        }
    
    def _transform_rooms_list(self, rooms: list) -> list:
        """Transform list of rooms."""
        return [self._transform_room(r) for r in rooms]
    
    # ── GET METHODS ────────────────────────────────────────────────────────
    def get_all(self) -> list:
        """Return all rooms."""
        rooms = RoomModel.get_all()
        return self._transform_rooms_list(rooms)
    
    def get_available(self, check_in: str, check_out: str) -> list:
        """
        Return rooms available for the given date range.
        Dates should be in YYYY-MM-DD format.
        """
        rooms = RoomModel.get_available(check_in, check_out)
        return self._transform_rooms_list(rooms)
    
    def get_by_id(self, room_id: int) -> dict | None:
        """Return a single room by ID."""
        room = RoomModel.get_by_id(room_id)
        return self._transform_room(room)
    
    # ── VALIDATION ─────────────────────────────────────────────────────────
    def _validate_room_data(self, room_number: str, room_type: str,
                            price: float, capacity: int) -> tuple:
        """Validate room data. Returns (is_valid, error_message)."""
        if not room_number or not room_number.strip():
            return (False, "Room number is required.")
        
        if room_type not in ['SINGLE', 'DOUBLE', 'DELUXE', 'SUITE']:
            return (False, "Invalid room type.")
        
        if price <= 0:
            return (False, "Price must be greater than 0.")
        
        if capacity < 1:
            return (False, "Capacity must be at least 1.")
        
        return (True, "")
    
    # ── CRUD OPERATIONS ────────────────────────────────────────────────────
    def create(self, room_number: str, room_type: str, price: float,
               capacity: int, description: str = "") -> tuple:
        """
        Create a new room.
        Returns (success, message)
        """
        # Validate input
        is_valid, error_msg = self._validate_room_data(
            room_number, room_type, price, capacity
        )
        if not is_valid:
            return (False, error_msg)
        
        # Create room
        success = RoomModel.create(room_number, room_type, price, 
                                    capacity, description)
        
        if success:
            return (True, f"Room {room_number} created successfully!")
        else:
            return (False, "Failed to create room. Please try again.")
    
    def update(self, room_id: int, room_number: str, room_type: str,
               price: float, capacity: int, description: str) -> tuple:
        """
        Update an existing room.
        Returns (success, message)
        """
        # Get old data for validation
        old_room = RoomModel.get_by_id(room_id)
        if not old_room:
            return (False, "Room not found.")
        
        # Validate input
        is_valid, error_msg = self._validate_room_data(
            room_number, room_type, price, capacity
        )
        if not is_valid:
            return (False, error_msg)
        
        # Update room
        success = RoomModel.update(room_id, room_number, room_type,
                                    price, capacity, description)
        
        if success:
            return (True, f"Room {room_number} updated successfully!")
        else:
            return (False, "Failed to update room. Please try again.")
    
    def update_status(self, room_id: int, status: str) -> tuple:
        """
        Update room status.
        Returns (success, message)
        """
        if status not in ['AVAILABLE', 'OCCUPIED', 'MAINTENANCE']:
            return (False, "Invalid status value.")
        
        room = RoomModel.get_by_id(room_id)
        if not room:
            return (False, "Room not found.")
        
        success = RoomModel.update_status(room_id, status)
        
        if success:
            return (True, f"Room {room['room_number']} status updated to {status}.")
        else:
            return (False, "Failed to update room status.")
    
    def delete(self, room_id: int) -> tuple:
        """
        Permanently delete a room.
        Returns (success, message)
        """
        room = RoomModel.get_by_id(room_id)
        if not room:
            return (False, "Room not found.")
        
        success = RoomModel.delete(room_id)
        
        if success:
            return (True, f"Room {room['room_number']} deleted successfully.")
        else:
            return (False, "Failed to delete room. Please try again.")


# ── Singleton instance ──────────────────────────────────────────────────────
_room_controller = RoomController()


def get_room_controller():
    """Return the singleton room controller instance."""
    return _room_controller