"""
Service Model for Hotel Management System
Handles CRUD operations for services with soft delete support
"""

from typing import Optional, List, Dict, Any
from models.base_model import BaseModel
from config.database import DatabaseQuery


class ServiceModel(BaseModel):
    """
    Model for service operations
    Table: services
    """
    
    table_name = 'services'
    primary_key = 'service_id'
    
    # Columns that should be excluded from automatic updates
    exclude_from_update = ['service_id', 'created_at']
    
    @classmethod
    def get_all_active(cls) -> List[Dict[str, Any]]:
        """Get all active services"""
        query = """
            SELECT 
                service_id as id,
                name,
                price,
                duration,
                status
            FROM services 
            WHERE is_deleted = FALSE AND status = 'Active'
            ORDER BY name
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_all_with_details(cls, status_filter: str = "ALL") -> List[Dict[str, Any]]:
        """Get all services with optional status filter"""
        if status_filter and status_filter != "ALL":
            query = """
                SELECT 
                    service_id as id,
                    name,
                    price,
                    duration,
                    status
                FROM services 
                WHERE is_deleted = FALSE AND status = %s
                ORDER BY name
            """
            return DatabaseQuery.fetch_all(query, (status_filter,))
        
        query = """
            SELECT 
                service_id as id,
                name,
                price,
                duration,
                status
            FROM services 
            WHERE is_deleted = FALSE
            ORDER BY name
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_deleted_services(cls, search_text: str = None) -> List[Dict[str, Any]]:
        """Get deleted services with optional search"""
        if search_text:
            query = """
                SELECT 
                    service_id as id,
                    name,
                    price,
                    duration,
                    status,
                    deleted_at
                FROM services 
                WHERE is_deleted = TRUE AND name LIKE %s
                ORDER BY deleted_at DESC
            """
            like_term = f"%{search_text}%"
            return DatabaseQuery.fetch_all(query, (like_term,))
        
        query = """
            SELECT 
                service_id as id,
                name,
                price,
                duration,
                status,
                deleted_at
            FROM services 
            WHERE is_deleted = TRUE
            ORDER BY deleted_at DESC
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_service_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """Get service by name"""
        query = """
            SELECT 
                service_id as id,
                name,
                price,
                duration,
                status
            FROM services 
            WHERE name = %s AND is_deleted = FALSE
        """
        return DatabaseQuery.fetch_one(query, (name.strip(),))
    
    @classmethod
    def get_all_for_combo(cls) -> List[Dict[str, Any]]:
        """Get services formatted for combo box"""
        query = """
            SELECT 
                service_id as id,
                name,
                price
            FROM services 
            WHERE is_deleted = FALSE AND status = 'Active'
            ORDER BY name
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def count_active_services(cls) -> int:
        """Get total number of active services"""
        query = """
            SELECT COUNT(*) as total
            FROM services 
            WHERE is_deleted = FALSE AND status = 'Active'
        """
        result = DatabaseQuery.fetch_one(query)
        return result['total'] if result else 0
    
    @classmethod
    def get_by_id(cls, service_id: int) -> Optional[Dict[str, Any]]:
        """Get service by ID"""
        return cls.find(service_id)
    
    @classmethod
    def create_service(cls, data: Dict[str, Any]) -> Optional[int]:
        """Create a new service with validation"""
        required = ['name', 'price']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"{field} is required")
        
        # Validate price
        try:
            price = float(data['price'])
            if price <= 0:
                raise ValueError("Price must be greater than 0")
        except ValueError:
            raise ValueError("Price must be a valid number")
        
        # Prepare data for insert
        insert_data = {
            'name': data['name'].strip(),
            'price': price,
            'duration': data.get('duration', 0),
            'status': data.get('status', 'Active'),
            'is_deleted': 0
        }
        
        return cls.create(insert_data)
    
    @classmethod
    def update_service(cls, service_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing service"""
        existing = cls.find(service_id)
        if not existing:
            raise ValueError(f"Service with ID {service_id} not found")
        
        # Validate price if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price <= 0:
                    raise ValueError("Price must be greater than 0")
                data['price'] = price
            except ValueError:
                raise ValueError("Price must be a valid number")
        
        # Prepare data for update
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name'].strip()
        if 'price' in data:
            update_data['price'] = data['price']
        if 'duration' in data:
            update_data['duration'] = data['duration']
        if 'status' in data:
            update_data['status'] = data['status']
        
        return cls.update(service_id, update_data)
    
    @classmethod
    def delete_service(cls, service_id: int) -> bool:
        """Soft delete a service"""
        return cls.delete(service_id)
    
    @classmethod
    def restore_service(cls, service_id: int) -> bool:
        """Restore a soft-deleted service"""
        return cls.restore(service_id)
    
    @classmethod
    def search_services(cls, keyword: str, status_filter: str = "ALL") -> List[Dict[str, Any]]:
        """Search services by name with optional status filter"""
        if not keyword:
            return cls.get_all_with_details(status_filter)
        
        if status_filter and status_filter != "ALL":
            query = """
                SELECT 
                    service_id as id,
                    name,
                    price,
                    duration,
                    status
                FROM services 
                WHERE is_deleted = FALSE 
                AND status = %s
                AND name LIKE %s
                ORDER BY name
            """
            like_term = f"%{keyword}%"
            return DatabaseQuery.fetch_all(query, (status_filter, like_term))
        
        query = """
            SELECT 
                service_id as id,
                name,
                price,
                duration,
                status
            FROM services 
            WHERE is_deleted = FALSE 
            AND name LIKE %s
            ORDER BY name
        """
        like_term = f"%{keyword}%"
        return DatabaseQuery.fetch_all(query, (like_term,))
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get service statistics"""
        query = """
            SELECT 
                COUNT(*) as total_services,
                SUM(CASE WHEN status = 'Active' AND is_deleted = FALSE THEN 1 ELSE 0 END) as active_services,
                SUM(CASE WHEN is_deleted = TRUE THEN 1 ELSE 0 END) as deleted_services
            FROM services
        """
        result = DatabaseQuery.fetch_one(query)
        return result or {}