"""
Account Controller - Handles admin login and registration logic
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtCore import QObject, pyqtSignal
import hashlib
import re
from datetime import datetime

# Import database connection
from config.database import get_connection


class AccountController(QObject):
    """
    Controller for admin account management (login and registration)
    """
    
    # Signals
    login_successful = pyqtSignal(dict)  # Emits user data on successful login
    registration_successful = pyqtSignal(str)  # Emits email on successful registration
    login_failed = pyqtSignal(str)  # Emits error message
    registration_failed = pyqtSignal(str)  # Emits error message
    
    def __init__(self):
        super().__init__()
        self.current_user = None
        
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple:
        """
        Validate password strength
        Returns (is_valid, error_message)
        """
        if len(password) < 6:
            return False, "Password must be at least 6 characters long."
        if len(password) > 50:
            return False, "Password must be less than 50 characters."
        return True, ""
    
    def check_email_exists(self, email: str) -> bool:
        """Check if email already exists in database"""
        conn = get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            query = "SELECT user_id FROM users WHERE email = %s AND role = 'Admin' AND is_deleted = 0"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
            return result is not None
        except Exception as e:
            print(f"Error checking email: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def register_admin(self, user_data: dict) -> tuple:
        """
        Register a new admin user
        Returns (success, message, user_id)
        """
        try:
            # Validate email
            if not self.validate_email(user_data['email']):
                return False, "Invalid email format.", None
            
            # Validate password
            is_valid, password_error = self.validate_password(user_data['password'])
            if not is_valid:
                return False, password_error, None
            
            # Check if email already exists
            if self.check_email_exists(user_data['email']):
                return False, "Email already registered.", None
            
            # Hash password
            hashed_password = self.hash_password(user_data['password'])
            
            # Insert into database - using your actual table structure
            conn = get_connection()
            if not conn:
                return False, "Database connection failed.", None
            
            try:
                cursor = conn.cursor()
                # Note: Using user_id, is_deleted instead of id and status
                query = """
                    INSERT INTO users 
                    (first_name, last_name, email, phone, password, role, is_deleted, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    user_data['first_name'],
                    user_data['last_name'],
                    user_data['email'],
                    user_data['phone'],
                    hashed_password,
                    'Admin',
                    0,  # is_deleted = 0 (not deleted)
                    datetime.now(),
                    datetime.now()
                ))
                conn.commit()
                user_id = cursor.lastrowid
                
                # Emit success signal
                self.registration_successful.emit(user_data['email'])
                
                return True, "Registration successful! Please login.", user_id
                
            except Exception as e:
                conn.rollback()
                print(f"Database error: {e}")
                error_msg = f"Registration failed: {str(e)}"
                self.registration_failed.emit(error_msg)
                return False, error_msg, None
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Registration error: {e}")
            error_msg = f"Registration error: {str(e)}"
            self.registration_failed.emit(error_msg)
            return False, error_msg, None
    
    def login_admin(self, email: str, password: str) -> tuple:
        """
        Authenticate admin user
        Returns (success, message, user_data)
        """
        try:
            # Validate email
            if not self.validate_email(email):
                error_msg = "Invalid email format."
                self.login_failed.emit(error_msg)
                return False, error_msg, None
            
            # Hash the provided password
            hashed_password = self.hash_password(password)
            
            # Query database - using your actual table structure
            conn = get_connection()
            if not conn:
                error_msg = "Database connection failed."
                self.login_failed.emit(error_msg)
                return False, error_msg, None
            
            try:
                cursor = conn.cursor()
                # Note: Using user_id instead of id, checking is_deleted = 0
                query = """
                    SELECT user_id, first_name, last_name, email, phone, role, is_deleted
                    FROM users 
                    WHERE email = %s AND password = %s AND role = 'Admin' AND is_deleted = 0
                """
                cursor.execute(query, (email, hashed_password))
                user = cursor.fetchone()
                
                if user:
                    user_data = {
                        'id': user[0],
                        'first_name': user[1],
                        'last_name': user[2],
                        'email': user[3],
                        'phone': user[4],
                        'role': user[5],
                        'is_deleted': user[6]
                    }
                    self.current_user = user_data
                    success_msg = "Login successful!"
                    self.login_successful.emit(user_data)
                    return True, success_msg, user_data
                else:
                    error_msg = "Invalid email or password."
                    self.login_failed.emit(error_msg)
                    return False, error_msg, None
                    
            except Exception as e:
                print(f"Database error: {e}")
                error_msg = f"Login failed: {str(e)}"
                self.login_failed.emit(error_msg)
                return False, error_msg, None
            finally:
                conn.close()
                
        except Exception as e:
            print(f"Login error: {e}")
            error_msg = f"Login error: {str(e)}"
            self.login_failed.emit(error_msg)
            return False, error_msg, None
    
    def get_current_user(self):
        """Return the currently logged in user"""
        return self.current_user
    
    def logout(self):
        """Logout the current user"""
        self.current_user = None
        return True, "Logged out successfully."


# Singleton pattern - create a single instance to be shared across the application
_account_controller = None

def get_account_controller():
    """
    Get or create the account controller singleton
    This ensures only one instance is used throughout the application
    """
    global _account_controller
    if _account_controller is None:
        _account_controller = AccountController()
    return _account_controller