"""
Base Model Class for Hotel Management System
Provides common CRUD operations for all models
"""

from typing import Optional, List, Dict, Any
from config.database import DatabaseQuery


class BaseModel:
    """
    Base model class with common database operations
    All models should inherit from this class
    """
    
    # Table name - must be overridden by child classes
    table_name: str = None
    
    # Primary key column name - defaults to 'id'
    primary_key: str = 'id'
    
    # Columns that should be excluded from automatic updates
    exclude_from_update: List[str] = ['created_at']
    
    @classmethod
    def _get_table_name(cls) -> str:
        """Get the table name, raise error if not defined"""
        if cls.table_name is None:
            raise NotImplementedError(f"{cls.__name__} must define table_name")
        return cls.table_name
    
    @classmethod
    def find(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """Find a record by its primary key"""
        query = f"SELECT * FROM {cls._get_table_name()} WHERE {cls.primary_key} = %s"
        params = [record_id]
        
        # Only add is_deleted condition if column exists
        if cls._has_deleted_column():
            query += " AND is_deleted = FALSE"
        
        return DatabaseQuery.fetch_one(query, tuple(params))
    
    @classmethod
    def find_deleted(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """Find a deleted record by its primary key"""
        query = f"SELECT * FROM {cls._get_table_name()} WHERE {cls.primary_key} = %s AND is_deleted = TRUE"
        return DatabaseQuery.fetch_one(query, (record_id,))
    
    @classmethod
    def all(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all active records"""
        query = f"SELECT * FROM {cls._get_table_name()} WHERE is_deleted = FALSE LIMIT %s OFFSET %s"
        return DatabaseQuery.fetch_all(query, (limit, offset))
    
    @classmethod
    def all_deleted(cls, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get all deleted records"""
        query = f"SELECT * FROM {cls._get_table_name()} WHERE is_deleted = TRUE LIMIT %s OFFSET %s"
        return DatabaseQuery.fetch_all(query, (limit, offset))
    
    @classmethod
    def create(cls, data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new record
        Returns the new record's ID or None if failed
        """
        # Remove fields that shouldn't be inserted
        data = {k: v for k, v in data.items() if v is not None}
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        
        query = f"INSERT INTO {cls._get_table_name()} ({columns}) VALUES ({placeholders})"
        return DatabaseQuery.insert_and_get_id(query, values)
    
    @classmethod
    def update(cls, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Update a record
        Returns True if successful
        """
        # Remove excluded fields
        for field in cls.exclude_from_update:
            data.pop(field, None)
        
        # Remove None values (keep as is)
        data = {k: v for k, v in data.items() if v is not None}
        
        if not data:
            return True  # Nothing to update
        
        set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
        values = tuple(data.values()) + (record_id,)
        
        query = f"UPDATE {cls._get_table_name()} SET {set_clause} WHERE {cls.primary_key} = %s AND is_deleted = FALSE"
        return DatabaseQuery.execute_query(query, values)
    
    @classmethod
    def delete(cls, record_id: int) -> bool:
        """
        Soft delete a record (set is_deleted = TRUE)
        Returns True if successful
        """
        query = f"UPDATE {cls._get_table_name()} SET is_deleted = TRUE, deleted_at = NOW() WHERE {cls.primary_key} = %s AND is_deleted = FALSE"
        return DatabaseQuery.execute_query(query, (record_id,))
    
    @classmethod
    def restore(cls, record_id: int) -> bool:
        """
        Restore a soft-deleted record
        Returns True if successful
        """
        query = f"UPDATE {cls._get_table_name()} SET is_deleted = FALSE, deleted_at = NULL WHERE {cls.primary_key} = %s AND is_deleted = TRUE"
        return DatabaseQuery.execute_query(query, (record_id,))
    
    @classmethod
    def hard_delete(cls, record_id: int) -> bool:
        """
        Permanently delete a record
        Use with caution!
        """
        query = f"DELETE FROM {cls._get_table_name()} WHERE {cls.primary_key} = %s"
        return DatabaseQuery.execute_query(query, (record_id,))
    
    @classmethod
    def search(cls, search_term: str, columns: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search records across specified columns
        """
        if not search_term or not columns:
            return []
        
        conditions = ' OR '.join([f"{col} LIKE %s" for col in columns])
        like_term = f"%{search_term}%"
        params = [like_term] * len(columns)
        
        query = f"SELECT * FROM {cls._get_table_name()} WHERE is_deleted = FALSE AND ({conditions}) LIMIT %s"
        params.append(limit)
        
        return DatabaseQuery.fetch_all(query, tuple(params))
    
    @classmethod
    def count(cls) -> int:
        """Get total count of active records"""
        query = f"SELECT COUNT(*) as total FROM {cls._get_table_name()} WHERE is_deleted = FALSE"
        result = DatabaseQuery.fetch_one(query)
        return result['total'] if result else 0
    
    @classmethod
    def exists(cls, field: str, value: Any) -> bool:
        """
        Check if a record exists with given field value
        """
        query = f"SELECT COUNT(*) as count FROM {cls._get_table_name()} WHERE {field} = %s AND is_deleted = FALSE"
        result = DatabaseQuery.fetch_one(query, (value,))
        return result['count'] > 0 if result else False
    
    
    @classmethod
    def _has_deleted_column(cls) -> bool:
        """Check if table has is_deleted column"""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME = %s 
                AND COLUMN_NAME = 'is_deleted'
            """
            result = DatabaseQuery.fetch_one(query, (cls._get_table_name(),))
            return result and result['count'] > 0
        except:
            return False