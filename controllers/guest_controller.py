"""
Guest Controller
================
Manages guest operations, connects GuestModel with views.
Handles validation, data transformation, and audit logging.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.guest_model import GuestModel
from models.admin_log_model import AdminLogModel
from controllers.auth_controller import get_auth_controller
import json


class GuestController:
    """Controller for guest management operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── DATA TRANSFORMATION ────────────────────────────────────────────────
    def _transform_guest(self, guest: dict) -> dict:
        """Convert guest_id to id for view compatibility."""
        if not guest:
            return None
        return {
            'id': guest['guest_id'],
            'first_name': guest['first_name'],
            'last_name': guest['last_name'],
            'email': guest['email'],
            'phone': guest['phone'],
            'address': guest['address']
        }
    
    def _transform_guests_list(self, guests: list) -> list:
        """Transform list of guests."""
        return [self._transform_guest(g) for g in guests]
    
    # ── GET METHODS ────────────────────────────────────────────────────────
    def get_all_active(self) -> list:
        """Return all active (non-deleted) guests."""
        guests = GuestModel.get_all_active()
        return self._transform_guests_list(guests)
    
    def get_all_deleted(self) -> list:
        """Return all deleted guests."""
        guests = GuestModel.get_all_deleted()
        return self._transform_guests_list(guests)
    
    def get_by_id(self, guest_id: int) -> dict | None:
        """Return a single guest by ID."""
        guest = GuestModel.get_by_id(guest_id)
        return self._transform_guest(guest)
    
    def search(self, keyword: str) -> list:
        """Search active guests by name or email."""
        if not keyword:
            return self.get_all_active()
        
        all_guests = self.get_all_active()
        keyword_lower = keyword.lower()
        return [g for g in all_guests if keyword_lower in g['first_name'].lower() or 
                keyword_lower in g['last_name'].lower() or
                keyword_lower in g['email'].lower()]
    
    # ── VALIDATION ─────────────────────────────────────────────────────────
    def _validate_guest_data(self, first_name: str, last_name: str, 
                              email: str, phone: str, address: str,
                              exclude_id: int = None) -> tuple:
        """Validate guest data. Returns (is_valid, error_message)."""
        if not first_name or not first_name.strip():
            return (False, "First name is required.")
        
        if not last_name or not last_name.strip():
            return (False, "Last name is required.")
        
        if not email or not email.strip():
            return (False, "Email address is required.")
        
        # Check email uniqueness
        if GuestModel.email_exists(email, exclude_id):
            return (False, "Email address is already registered.")
        
        if not phone or not phone.strip():
            return (False, "Contact number is required.")
        
        if not address or not address.strip():
            return (False, "Address is required.")
        
        return (True, "")
    
    # ── CRUD OPERATIONS ────────────────────────────────────────────────────
    def create(self, first_name: str, last_name: str, email: str,
               phone: str, address: str) -> tuple:
        """
        Create a new guest.
        Returns (success, message)
        """
        # Validate input
        is_valid, error_msg = self._validate_guest_data(
            first_name, last_name, email, phone, address
        )
        if not is_valid:
            return (False, error_msg)
        
        # Create guest
        success = GuestModel.create(first_name, last_name, email, phone, address)
        
        if success:
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="CREATE_GUEST",
                    description=f"Created guest: {first_name} {last_name} (Email: {email})"
                )
            return (True, f"Guest '{first_name} {last_name}' created successfully!")
        else:
            return (False, "Failed to create guest. Please try again.")
    
    def update(self, guest_id: int, first_name: str, last_name: str,
               email: str, phone: str, address: str) -> tuple:
        """
        Update an existing guest.
        Returns (success, message)
        """
        # Get old data for logging
        old_guest = GuestModel.get_by_id(guest_id)
        if not old_guest:
            return (False, "Guest not found.")
        
        # Validate input
        is_valid, error_msg = self._validate_guest_data(
            first_name, last_name, email, phone, address, guest_id
        )
        if not is_valid:
            return (False, error_msg)
        
        # Update guest
        success = GuestModel.update(guest_id, first_name, last_name, 
                                     email, phone, address)
        
        if success:
            # Log the action with details
            user = get_auth_controller().get_current_user()
            if user:
                changes = {
                    'old': {
                        'first_name': old_guest['first_name'],
                        'last_name': old_guest['last_name'],
                        'email': old_guest['email'],
                        'phone': old_guest['phone'],
                        'address': old_guest['address']
                    },
                    'new': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone': phone,
                        'address': address
                    }
                }
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="UPDATE_GUEST",
                    description=f"Updated guest ID {guest_id}: {json.dumps(changes)}"
                )
            return (True, f"Guest '{first_name} {last_name}' updated successfully!")
        else:
            return (False, "Failed to update guest. Please try again.")
    
    def soft_delete(self, guest_id: int) -> tuple:
        """
        Soft delete a guest.
        Returns (success, message)
        """
        # Get guest name for logging
        guest = GuestModel.get_by_id(guest_id)
        if not guest:
            return (False, "Guest not found.")
        
        success = GuestModel.soft_delete(guest_id)
        
        if success:
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="DELETE_GUEST",
                    description=f"Deleted guest: {guest['first_name']} {guest['last_name']} (ID: {guest_id})"
                )
            return (True, f"Guest '{guest['first_name']} {guest['last_name']}' deleted successfully.")
        else:
            return (False, "Failed to delete guest. Please try again.")
    
    def restore(self, guest_id: int) -> tuple:
        """
        Restore a deleted guest.
        Returns (success, message)
        """
        # Get guest name for logging
        guest = GuestModel.get_by_id(guest_id)
        if not guest:
            return (False, "Guest not found.")
        
        success = GuestModel.restore(guest_id)
        
        if success:
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="RESTORE_GUEST",
                    description=f"Restored guest: {guest['first_name']} {guest['last_name']} (ID: {guest_id})"
                )
            return (True, f"Guest '{guest['first_name']} {guest['last_name']}' restored successfully.")
        else:
            return (False, "Failed to restore guest. Please try again.")


# ── Singleton instance ──────────────────────────────────────────────────────
_guest_controller = GuestController()


def get_guest_controller():
    """Return the singleton guest controller instance."""
    return _guest_controller