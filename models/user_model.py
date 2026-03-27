"""
User Model for Hotel Management System
Handles CRUD operations for users with soft delete support
"""

from typing import Optional, List, Dict, Any
from models.base_model import BaseModel
from config.database import DatabaseQuery


class UserModel(BaseModel):
    """
    Model for user operations
    Table: users
    """
    
    table_name = 'users'
    primary_key = 'user_id'
    
    # Columns that should be excluded from automatic updates
    exclude_from_update = ['user_id', 'created_at']
    
    @classmethod
    def get_all_active(cls) -> List[Dict[str, Any]]:
        """Get all active (non-deleted) users"""
        query = """
            SELECT 
                user_id as id,
                first_name,
                last_name,
                email,
                phone,
                role,
                created_at
            FROM users 
            WHERE is_deleted = FALSE
            ORDER BY role, last_name, first_name
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = """
            SELECT 
                user_id as id,
                first_name,
                last_name,
                email,
                phone,
                role,
                is_deleted
            FROM users 
            WHERE email = %s
        """
        return DatabaseQuery.fetch_one(query, (email.strip().lower(),))
    
    @classmethod
    def get_by_role(cls, role: str) -> List[Dict[str, Any]]:
        """Get users by role"""
        query = """
            SELECT 
                user_id as id,
                first_name,
                last_name,
                email,
                phone,
                role
            FROM users 
            WHERE role = %s AND is_deleted = FALSE
            ORDER BY last_name, first_name
        """
        return DatabaseQuery.fetch_all(query, (role,))
    
    @classmethod
    def count_staff(cls) -> int:
        """Get total number of active staff members"""
        query = """
            SELECT COUNT(*) as total
            FROM users 
            WHERE role = 'Staff' AND is_deleted = FALSE
        """
        result = DatabaseQuery.fetch_one(query)
        return result['total'] if result else 0
    
    @classmethod
    def count_admins(cls) -> int:
        """Get total number of active admin users"""
        query = """
            SELECT COUNT(*) as total
            FROM users 
            WHERE role = 'Admin' AND is_deleted = FALSE
        """
        result = DatabaseQuery.fetch_one(query)
        return result['total'] if result else 0
    
    @classmethod
    def create_user(cls, data: Dict[str, Any]) -> Optional[int]:
        """Create a new user with validation"""
        required = ['first_name', 'last_name', 'email', 'phone', 'password', 'role']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"{field} is required")
        
        # Check if email already exists
        existing = cls.get_by_email(data['email'])
        if existing:
            raise ValueError(f"Email '{data['email']}' already exists")
        
        # Prepare data for insert
        insert_data = {
            'first_name': data['first_name'].strip(),
            'last_name': data['last_name'].strip(),
            'email': data['email'].strip().lower(),
            'phone': data['phone'].strip(),
            'password': data['password'],  # Should be hashed already
            'role': data['role'],
            'is_deleted': 0
        }
        
        return cls.create(insert_data)
    
    @classmethod
    def update_user(cls, user_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing user"""
        existing = cls.find(user_id)
        if not existing:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Check if email is being changed and already exists
        if 'email' in data:
            email_check = cls.get_by_email(data['email'])
            if email_check and email_check['id'] != user_id:
                raise ValueError(f"Email '{data['email']}' already exists")
        
        # Prepare data for update
        update_data = {}
        if 'first_name' in data:
            update_data['first_name'] = data['first_name'].strip()
        if 'last_name' in data:
            update_data['last_name'] = data['last_name'].strip()
        if 'email' in data:
            update_data['email'] = data['email'].strip().lower()
        if 'phone' in data:
            update_data['phone'] = data['phone'].strip()
        if 'password' in data:
            update_data['password'] = data['password']
        if 'role' in data:
            update_data['role'] = data['role']
        
        return cls.update(user_id, update_data)
    
    @classmethod
    def delete_user(cls, user_id: int) -> bool:
        """Soft delete a user"""
        return cls.delete(user_id)
    
    @classmethod
    def restore_user(cls, user_id: int) -> bool:
        """Restore a soft-deleted user"""
        return cls.restore(user_id)
    
    @classmethod
    def search_users(cls, keyword: str) -> List[Dict[str, Any]]:
        """Search users by name, email, or phone"""
        if not keyword:
            return cls.get_all_active()
        
        query = """
            SELECT 
                user_id as id,
                first_name,
                last_name,
                email,
                phone,
                role
            FROM users 
            WHERE is_deleted = FALSE 
            AND (first_name LIKE %s 
                 OR last_name LIKE %s 
                 OR email LIKE %s
                 OR phone LIKE %s)
            ORDER BY role, last_name, first_name
        """
        like_term = f"%{keyword}%"
        return DatabaseQuery.fetch_all(query, (like_term, like_term, like_term, like_term))
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get user statistics"""
        query = """
            SELECT 
                COUNT(*) as total_users,
                SUM(CASE WHEN role = 'Admin' THEN 1 ELSE 0 END) as admin_count,
                SUM(CASE WHEN role = 'Staff' THEN 1 ELSE 0 END) as staff_count,
                SUM(CASE WHEN is_deleted = TRUE THEN 1 ELSE 0 END) as deleted_users
            FROM users
        """
        result = DatabaseQuery.fetch_one(query)
        return result or {}