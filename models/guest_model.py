"""
Guest Model for Hotel Management System
Handles CRUD operations for guests with soft delete support
"""

from typing import Optional, List, Dict, Any
from models.base_model import BaseModel
from config.database import DatabaseQuery


class GuestModel(BaseModel):
    """
    Model for guest operations
    Table: guests
    """
    
    table_name = 'guests'
    primary_key = 'guest_id'
    
    # Columns that should be excluded from automatic updates
    exclude_from_update = ['guest_id', 'created_at']
    
    @classmethod
    def get_all_active(cls) -> List[Dict[str, Any]]:
        """Get all active (non-deleted) guests"""
        query = """
            SELECT 
                guest_id as id,
                first_name,
                last_name,
                email,
                phone,
                address
            FROM guests 
            WHERE is_deleted = FALSE
            ORDER BY last_name, first_name
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_all_for_combo(cls) -> List[Dict[str, Any]]:
        """Get guests formatted for combo box (id, display_name)"""
        query = """
            SELECT 
                guest_id as id,
                CONCAT(first_name, ' ', last_name) as name
            FROM guests 
            WHERE is_deleted = FALSE
            ORDER BY last_name, first_name
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_by_id(cls, guest_id: int) -> Optional[Dict[str, Any]]:
        """Get guest by ID"""
        return cls.find(guest_id)
    
    @classmethod
    def create_guest(cls, data: Dict[str, Any]) -> Optional[int]:
        """Create a new guest with validation"""
        required = ['first_name', 'last_name', 'email', 'phone', 'address']
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
            'address': data['address'].strip(),
            'is_deleted': 0
        }
        
        return cls.create(insert_data)
    
    @classmethod
    def update_guest(cls, guest_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing guest"""
        existing = cls.find(guest_id)
        if not existing:
            raise ValueError(f"Guest with ID {guest_id} not found")
        
        # Check if email is being changed and already exists
        if 'email' in data:
            email_check = cls.get_by_email(data['email'])
            if email_check and email_check['id'] != guest_id:
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
        if 'address' in data:
            update_data['address'] = data['address'].strip()
        
        return cls.update(guest_id, update_data)
    
    @classmethod
    def delete_guest(cls, guest_id: int) -> bool:
        """Soft delete a guest"""
        return cls.delete(guest_id)
    
    @classmethod
    def get_by_email(cls, email: str) -> Optional[Dict[str, Any]]:
        """Get guest by email"""
        query = """
            SELECT 
                guest_id as id,
                first_name,
                last_name,
                email,
                phone,
                address
            FROM guests 
            WHERE email = %s AND is_deleted = FALSE
        """
        return DatabaseQuery.fetch_one(query, (email.strip().lower(),))
    
    @classmethod
    def search_guests(cls, keyword: str) -> List[Dict[str, Any]]:
        """Search guests by name or email"""
        if not keyword:
            return cls.get_all_active()
        
        query = """
            SELECT 
                guest_id as id,
                first_name,
                last_name,
                email,
                phone,
                address
            FROM guests 
            WHERE is_deleted = FALSE 
            AND (first_name LIKE %s 
                 OR last_name LIKE %s 
                 OR email LIKE %s
                 OR phone LIKE %s)
            ORDER BY last_name, first_name
        """
        like_term = f"%{keyword}%"
        return DatabaseQuery.fetch_all(query, (like_term, like_term, like_term, like_term))
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get guest statistics"""
        query = """
            SELECT 
                COUNT(*) as total_guests,
                COUNT(CASE WHEN is_deleted = TRUE THEN 1 END) as deleted_guests
            FROM guests
        """
        result = DatabaseQuery.fetch_one(query)
        return result or {}