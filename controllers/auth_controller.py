"""
Authentication Controller
=========================
Handles user authentication, registration, and session management.
Connects login/registration views with UserModel.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.user_model import UserModel
from utils.password_utils import hash_password, verify_password
from utils.otp_utils import generate_otp, send_otp_email


class AuthController:
    """Controller for authentication-related operations."""
    
    _instance = None
    _current_user = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._pending_reset_email = None
        self._pending_reset_otp = None
    
    # ── LOGIN METHODS ───────────────────────────────────────────────────────
    def login_admin(self, email: str, password: str) -> tuple:
        """
        Authenticate admin user.
        Returns (success, message, user_data)
        """
        user = UserModel.get_by_email(email)
        
        if not user:
            return (False, "Account not found.", None)
        
        if user.get('is_deleted') == 1:
            return (False, "This account has been deactivated. Contact administrator.", None)
        
        if user.get('role') != 'Admin':
            return (False, "Invalid credentials. Please use Admin login.", None)
        
        if not verify_password(password, user.get('password', '')):
            return (False, "Invalid email or password.", None)
        
        # Store current user
        self._current_user = user
        
        return (True, "Login successful.", {
            'user_id': user['user_id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'role': user['role']
        })
    
    def login_staff(self, email: str, password: str) -> tuple:
        """
        Authenticate staff user.
        Returns (success, message, user_data)
        """
        user = UserModel.get_by_email(email)
        
        if not user:
            return (False, "Account not found.", None)
        
        if user.get('is_deleted') == 1:
            return (False, "This account has been deactivated. Contact administrator.", None)
        
        if user.get('role') != 'Staff':
            return (False, "Invalid credentials. Please use Staff login.", None)
        
        if not verify_password(password, user.get('password', '')):
            return (False, "Invalid email or password.", None)
        
        # Store current user
        self._current_user = user
        
        return (True, "Login successful.", {
            'user_id': user['user_id'],
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'email': user['email'],
            'role': user['role']
        })
    
    # ── REGISTRATION METHODS ────────────────────────────────────────────────
    def register_admin(self, first_name: str, last_name: str, 
                       email: str, phone: str, password: str) -> tuple:
        """
        Register a new admin account.
        Returns (success, message)
        """
        # Check if email already exists
        if UserModel.email_exists(email):
            return (False, "Email address is already registered.")
        
        # Validate password strength
        if len(password) < 6:
            return (False, "Password must be at least 6 characters long.")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        success = UserModel.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            role='Admin'
        )
        
        if success:
            return (True, "Admin account created successfully!")
        else:
            return (False, "Failed to create account. Please try again.")
    
    def register_staff(self, first_name: str, last_name: str,
                       email: str, phone: str, password: str) -> tuple:
        """
        Register a new staff account.
        Returns (success, message)
        """
        # Check if email already exists
        if UserModel.email_exists(email):
            return (False, "Email address is already registered.")
        
        # Validate password strength
        if len(password) < 6:
            return (False, "Password must be at least 6 characters long.")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        success = UserModel.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=password_hash,
            role='Staff'
        )
        
        if success:
            return (True, "Staff account created successfully!")
        else:
            return (False, "Failed to create account. Please try again.")
    
    # ── PASSWORD RESET METHODS ─────────────────────────────────────────────
    def request_password_reset(self, email: str) -> tuple:
        """
        Request OTP for password reset.
        Returns (success, message)
        """
        user = UserModel.get_by_email(email)
        
        if not user:
            return (False, "Email address not found in our records.")
        
        if user.get('is_deleted') == 1:
            return (False, "This account has been deactivated. Contact administrator.")
        
        # Generate OTP
        otp = generate_otp(6)
        self._pending_reset_email = email
        self._pending_reset_otp = otp
        
        # Send OTP via email
        sent = send_otp_email(email, otp)
        
        if sent:
            return (True, f"OTP sent to {email}. Please check your inbox.")
        else:
            return (False, "Failed to send OTP. Please check email configuration.")
    
    def verify_otp(self, otp: str) -> tuple:
        """
        Verify OTP for password reset.
        Returns (success, message)
        """
        if not self._pending_reset_otp:
            return (False, "No OTP request found. Please request a new OTP.")
        
        if self._pending_reset_otp != otp:
            return (False, "Invalid OTP. Please try again.")
        
        return (True, "OTP verified successfully.")
    
    def reset_password(self, new_password: str) -> tuple:
        """
        Reset password after OTP verification.
        Returns (success, message)
        """
        if not self._pending_reset_email:
            return (False, "No password reset request in progress.")
        
        if len(new_password) < 6:
            return (False, "Password must be at least 6 characters long.")
        
        # Get user
        user = UserModel.get_by_email(self._pending_reset_email)
        
        if not user:
            self._clear_reset_state()
            return (False, "User not found.")
        
        # Hash new password
        password_hash = hash_password(new_password)
        
        # Update password
        success = UserModel.update_password(user['user_id'], password_hash)
        
        if success:
            self._clear_reset_state()
            return (True, "Password reset successfully! You can now login.")
        else:
            return (False, "Failed to reset password. Please try again.")
    
    def _clear_reset_state(self):
        """Clear pending reset state."""
        self._pending_reset_email = None
        self._pending_reset_otp = None
    
    # ── SESSION METHODS ─────────────────────────────────────────────────────
    def get_current_user(self):
        """Return the currently logged-in user."""
        return self._current_user
    
    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self._current_user is not None
    
    def is_admin(self) -> bool:
        """Check if current user is admin."""
        return self._current_user and self._current_user.get('role') == 'Admin'
    
    def is_staff(self) -> bool:
        """Check if current user is staff."""
        return self._current_user and self._current_user.get('role') == 'Staff'
    
    def logout(self):
        """Log out the current user."""
        self._current_user = None
        self._clear_reset_state()


# ── Singleton instance ──────────────────────────────────────────────────────
_auth = AuthController()


def get_auth_controller():
    """Return the singleton auth controller instance."""
    return _auth