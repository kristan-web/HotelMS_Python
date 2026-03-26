"""
User Controller
================
Manages user operations for account management.
Connects UserModel with views, handles validation and audit logging.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user_model import UserModel
from models.admin_log_model import AdminLogModel
from controllers.auth_controller import get_auth_controller
from utils.password_utils import hash_password
import json


class UserController:
    """Controller for user management operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── DATA TRANSFORMATION ────────────────────────────────────────────────
    def _transform_user(self, user: dict) -> dict:
        """Convert user_id to id for view compatibility."""
        if not user:
            return None
        return {
            'user_id': user['user_id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'phone': user['phone'],
            'role': user['role']
        }
    
    def _transform_users_list(self, users: list) -> list:
        """Transform list of users."""
        return [self._transform_user(u) for u in users]
    
    # ── GET METHODS ────────────────────────────────────────────────────────
    def get_all_active(self) -> list:
        """Return all active (non-deleted) users."""
        users = UserModel.get_all_active()
        return self._transform_users_list(users)
    
    def get_all_deleted(self) -> list:
        """Return all deleted users."""
        users = UserModel.get_all_deleted()
        return self._transform_users_list(users)
    
    def get_by_id(self, user_id: int) -> dict | None:
        """Return a single user by ID."""
        user = UserModel.get_by_id(user_id)
        return self._transform_user(user)
    
    def search(self, keyword: str) -> list:
        """Search active users by name or email."""
        if not keyword:
            return self.get_all_active()
        
        all_users = self.get_all_active()
        keyword_lower = keyword.lower()
        return [u for u in all_users if keyword_lower in u['first_name'].lower() or 
                keyword_lower in u['last_name'].lower() or
                keyword_lower in u['email'].lower()]
    
    # ── VALIDATION ─────────────────────────────────────────────────────────
    def _validate_user_data(self, first_name: str, last_name: str,
                            email: str, phone: str, role: str,
                            exclude_id: int = None) -> tuple:
        """Validate user data. Returns (is_valid, error_message)."""
        if not first_name or not first_name.strip():
            return (False, "First name is required.")
        
        if not last_name or not last_name.strip():
            return (False, "Last name is required.")
        
        if not email or not email.strip():
            return (False, "Email address is required.")
        
        # Check email uniqueness
        if UserModel.email_exists(email, exclude_id):
            return (False, "Email address is already registered.")
        
        if not phone or not phone.strip():
            return (False, "Contact number is required.")
        
        if role not in ['Admin', 'Staff']:
            return (False, "Role must be either 'Admin' or 'Staff'.")
        
        return (True, "")
    
    # ── CRUD OPERATIONS ────────────────────────────────────────────────────
    def create(self, first_name: str, last_name: str, email: str,
               phone: str, password: str, role: str) -> tuple:
        """
        Create a new user.
        Returns (success, message)
        """
        # Validate input
        is_valid, error_msg = self._validate_user_data(
            first_name, last_name, email, phone, role
        )
        if not is_valid:
            return (False, error_msg)
        
        # Validate password
        if len(password) < 6:
            return (False, "Password must be at least 6 characters.")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        success = UserModel.create(first_name, last_name, email, phone, 
                                    password_hash, role)
        
        if success:
            # Log the action
            current_user = get_auth_controller().get_current_user()
            if current_user:
                AdminLogModel.log(
                    user_id=current_user['user_id'],
                    action="CREATE_USER",
                    description=f"Created {role} user: {first_name} {last_name} (Email: {email})"
                )
            return (True, f"{role} account '{first_name} {last_name}' created successfully!")
        else:
            return (False, "Failed to create user. Please try again.")
    
    def update(self, user_id: int, first_name: str, last_name: str,
               email: str, phone: str, role: str) -> tuple:
        """
        Update an existing user.
        Returns (success, message)
        """
        # Get old data for logging
        old_user = UserModel.get_by_id(user_id)
        if not old_user:
            return (False, "User not found.")
        
        # Cannot change own role if you're the only admin
        current_user = get_auth_controller().get_current_user()
        if current_user and current_user['user_id'] == user_id:
            if old_user['role'] != role:
                # Check if this would leave no admins
                admins = [u for u in self.get_all_active() if u['role'] == 'Admin']
                if len(admins) <= 1 and old_user['role'] == 'Admin' and role != 'Admin':
                    return (False, "Cannot change your own role. You are the only admin.")
        
        # Validate input
        is_valid, error_msg = self._validate_user_data(
            first_name, last_name, email, phone, role, user_id
        )
        if not is_valid:
            return (False, error_msg)
        
        # Update user
        success = UserModel.update(user_id, first_name, last_name, email, phone, role)
        
        if success:
            # Log the action with details
            if current_user:
                changes = {
                    'old': {
                        'first_name': old_user['first_name'],
                        'last_name': old_user['last_name'],
                        'email': old_user['email'],
                        'phone': old_user['phone'],
                        'role': old_user['role']
                    },
                    'new': {
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'phone': phone,
                        'role': role
                    }
                }
                AdminLogModel.log(
                    user_id=current_user['user_id'],
                    action="UPDATE_USER",
                    description=f"Updated user ID {user_id}: {json.dumps(changes)}"
                )
            return (True, f"User '{first_name} {last_name}' updated successfully!")
        else:
            return (False, "Failed to update user. Please try again.")
    
    def soft_delete(self, user_id: int) -> tuple:
        """
        Soft delete a user.
        Returns (success, message)
        """
        # Get user for logging
        user = UserModel.get_by_id(user_id)
        if not user:
            return (False, "User not found.")
        
        # Prevent deleting yourself
        current_user = get_auth_controller().get_current_user()
        if current_user and current_user['user_id'] == user_id:
            return (False, "You cannot delete your own account.")
        
        # Prevent deleting last admin
        if user['role'] == 'Admin':
            admins = [u for u in self.get_all_active() if u['role'] == 'Admin']
            if len(admins) <= 1:
                return (False, "Cannot delete the last admin account.")
        
        success = UserModel.soft_delete(user_id)
        
        if success:
            # Log the action
            if current_user:
                AdminLogModel.log(
                    user_id=current_user['user_id'],
                    action="DELETE_USER",
                    description=f"Deleted user: {user['first_name']} {user['last_name']} (ID: {user_id})"
                )
            return (True, f"User '{user['first_name']} {user['last_name']}' moved to deleted users.")
        else:
            return (False, "Failed to delete user. Please try again.")
    
    def restore(self, user_id: int) -> tuple:
        """
        Restore a deleted user.
        Returns (success, message)
        """
        # Get user for logging
        user = UserModel.get_by_id(user_id)
        if not user:
            return (False, "User not found.")
        
        success = UserModel.restore(user_id)
        
        if success:
            # Log the action
            current_user = get_auth_controller().get_current_user()
            if current_user:
                AdminLogModel.log(
                    user_id=current_user['user_id'],
                    action="RESTORE_USER",
                    description=f"Restored user: {user['first_name']} {user['last_name']} (ID: {user_id})"
                )
            return (True, f"User '{user['first_name']} {user['last_name']}' restored successfully.")
        else:
            return (False, "Failed to restore user. Please try again.")
    
    def reset_password(self, user_id: int, new_password: str) -> tuple:
        """
        Reset a user's password (admin only).
        Returns (success, message)
        """
        # Validate password
        if len(new_password) < 6:
            return (False, "Password must be at least 6 characters.")
        
        # Get user for logging
        user = UserModel.get_by_id(user_id)
        if not user:
            return (False, "User not found.")
        
        # Hash new password
        password_hash = hash_password(new_password)
        
        # Update password
        success = UserModel.update_password(user_id, password_hash)
        
        if success:
            # Log the action
            current_user = get_auth_controller().get_current_user()
            if current_user:
                AdminLogModel.log(
                    user_id=current_user['user_id'],
                    action="RESET_USER_PASSWORD",
                    description=f"Reset password for user: {user['first_name']} {user['last_name']} (ID: {user_id})"
                )
            return (True, f"Password reset successfully for {user['first_name']} {user['last_name']}.")
        else:
            return (False, "Failed to reset password.")


# ── Singleton instance ──────────────────────────────────────────────────────
_user_controller = UserController()


def get_user_controller():
    """Return the singleton user controller instance."""
    return _user_controller