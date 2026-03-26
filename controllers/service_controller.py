# controllers/service_controller.py
"""
Service Controller
==================
Manages service operations, connects ServiceModel with views.
Handles validation, data transformation, and audit logging.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.service_model import ServiceModel
from models.admin_log_model import AdminLogModel
from controllers.auth_controller import get_auth_controller
import json


class ServiceController:
    """Controller for service management operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── DATA TRANSFORMATION ────────────────────────────────────────────────
    def _transform_service(self, service: dict) -> dict:
        """Convert service_id to id for view compatibility."""
        if not service:
            return None
        return {
            'id': service['service_id'],
            'name': service['name'],
            'price': float(service['price']),
            'duration': service['duration'],
            'status': service['status']
        }
    
    def _transform_services_list(self, services: list) -> list:
        """Transform list of services."""
        return [self._transform_service(s) for s in services]
    
    # ── GET METHODS ────────────────────────────────────────────────────────
    def get_all_active(self) -> list:
        """Return all active (non-deleted) services."""
        services = ServiceModel.get_all_active()
        return self._transform_services_list(services)
    
    def get_all_deleted(self) -> list:
        """Return all deleted services."""
        services = ServiceModel.get_all_deleted()
        return self._transform_services_list(services)
    
    def get_by_id(self, service_id: int) -> dict | None:
        """Return a single service by ID."""
        service = ServiceModel.get_by_id(service_id)
        return self._transform_service(service)
    
    def search(self, keyword: str) -> list:
        """Search active services by name."""
        if not keyword:
            return self.get_all_active()
        
        all_services = self.get_all_active()
        keyword_lower = keyword.lower()
        return [s for s in all_services if keyword_lower in s['name'].lower()]
    
    # ── VALIDATION ─────────────────────────────────────────────────────────
    def _validate_service_data(self, name: str, price: float, duration: int) -> tuple:
        """Validate service data. Returns (is_valid, error_message)."""
        if not name or not name.strip():
            return (False, "Service name is required.")
        
        try:
            price_val = float(price)
            if price_val <= 0:
                return (False, "Price must be greater than 0.")
        except ValueError:
            return (False, "Invalid price format.")
        
        try:
            duration_val = int(duration)
            if duration_val <= 0:
                return (False, "Duration must be greater than 0.")
        except ValueError:
            return (False, "Invalid duration format.")
        
        return (True, "")
    
    # ── CRUD OPERATIONS ────────────────────────────────────────────────────
    def create(self, name: str, price: str, duration: str, status: str) -> tuple:
        """
        Create a new service.
        Returns (success, message)
        """
        # Validate input
        is_valid, error_msg = self._validate_service_data(name, price, duration)
        if not is_valid:
            return (False, error_msg)
        
        # Convert to proper types
        price_float = float(price)
        duration_int = int(duration)
        
        # Create service
        success = ServiceModel.create(name, price_float, duration_int, status)
        
        if success:
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="CREATE_SERVICE",
                    description=f"Created service: {name} (Price: {price_float}, Duration: {duration_int} mins)"
                )
            return (True, f"Service '{name}' created successfully!")
        else:
            return (False, "Failed to create service. Please try again.")
    
    def update(self, service_id: int, name: str, price: str, duration: str, status: str) -> tuple:
        """
        Update an existing service.
        Returns (success, message)
        """
        # Get old data for logging
        old_service = ServiceModel.get_by_id(service_id)
        if not old_service:
            return (False, "Service not found.")
        
        # Validate input
        is_valid, error_msg = self._validate_service_data(name, price, duration)
        if not is_valid:
            return (False, error_msg)
        
        # Convert to proper types
        price_float = float(price)
        duration_int = int(duration)
        
        # Update service
        success = ServiceModel.update(service_id, name, price_float, duration_int, status)
        
        if success:
            # Log the action with details
            user = get_auth_controller().get_current_user()
            if user:
                changes = {
                    'old': {
                        'name': old_service['name'],
                        'price': float(old_service['price']),
                        'duration': old_service['duration'],
                        'status': old_service['status']
                    },
                    'new': {
                        'name': name,
                        'price': price_float,
                        'duration': duration_int,
                        'status': status
                    }
                }
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="UPDATE_SERVICE",
                    description=f"Updated service ID {service_id}: {json.dumps(changes)}"
                )
            return (True, f"Service '{name}' updated successfully!")
        else:
            return (False, "Failed to update service. Please try again.")
    
    def soft_delete(self, service_id: int) -> tuple:
        """
        Soft delete a service.
        Returns (success, message)
        """
        # Get service name for logging
        service = ServiceModel.get_by_id(service_id)
        if not service:
            return (False, "Service not found.")
        
        success = ServiceModel.soft_delete(service_id)
        
        if success:
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="DELETE_SERVICE",
                    description=f"Deleted service: {service['name']} (ID: {service_id})"
                )
            return (True, f"Service '{service['name']}' deleted successfully.")
        else:
            return (False, "Failed to delete service. Please try again.")
    
    def restore(self, service_id: int) -> tuple:
        """
        Restore a deleted service.
        Returns (success, message)
        """
        # Get service name for logging
        service = ServiceModel.get_by_id(service_id)
        if not service:
            return (False, "Service not found.")
        
        success = ServiceModel.restore(service_id)
        
        if success:
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="RESTORE_SERVICE",
                    description=f"Restored service: {service['name']} (ID: {service_id})"
                )
            return (True, f"Service '{service['name']}' restored successfully.")
        else:
            return (False, "Failed to restore service. Please try again.")


# ── Singleton instance ──────────────────────────────────────────────────────
_service_controller = ServiceController()


def get_service_controller():
    """Return the singleton service controller instance."""
    return _service_controller