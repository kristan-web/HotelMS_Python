"""
Service Controller for Hotel Management System
Connects ServiceView and DeletedServicesView with ServiceModel
"""
import sys
import os
from typing import Optional, Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from models.service_model import ServiceModel
from views.ServiceManagement.ServiceView import ServiceView
from views.ServiceManagement.DeletedServicesView import DeletedServicesView


class ServiceController(QObject):
    """
    Controller for Service Management module
    Handles all service-related operations and view navigation
    """
    
    # Signal to notify main window
    back_to_main_requested = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.service_view = None
        self.deleted_view = None
        self.current_status_filter = "ALL"
        self.current_search_text = ""
        
        # Initialize views
        self._init_views()
        self._connect_signals()
        
        # Load initial data
        self.refresh_service_view()
    
    def _init_views(self):
        """Initialize all views"""
        self.service_view = ServiceView(self.main_window)
        self.deleted_view = DeletedServicesView(self.main_window)
        
        # Set window flags to make them dialogs that can be managed properly
        if self.main_window:
            self.service_view.setParent(self.main_window)
            self.deleted_view.setParent(self.main_window)
    
    def _connect_signals(self):
        """Connect view signals to controller methods"""
        # ServiceView signals
        self.service_view.add_requested.connect(self.add_service)
        self.service_view.edit_requested.connect(self.edit_service)
        self.service_view.delete_requested.connect(self.delete_service)
        self.service_view.back_requested.connect(self.go_back)
        self.service_view.show_deleted_requested.connect(self.show_deleted_view)
        
        # Connect search and filter functionality for ServiceView
        self.service_view.search_changed.connect(self.on_search_changed)
        self.service_view.filter_changed.connect(self.on_filter_changed)
        
        # DeletedServicesView signals
        self.deleted_view.restore_requested.connect(self.restore_service)
        self.deleted_view.back_requested.connect(self.show_service_view)
        self.deleted_view.search_changed.connect(self.on_deleted_search_changed)
    
    # ==================== Search and Filter Functionality ====================
    
    def on_search_changed(self, search_text: str):
        """Handle search text changes in main service view"""
        self.current_search_text = search_text
        self.refresh_service_view()
    
    def on_filter_changed(self, status: str):
        """Handle status filter changes"""
        self.current_status_filter = status
        print(f"Filter changed to: {status}")  # Debug log
        self.refresh_service_view()
    
    def on_deleted_search_changed(self, search_text: str):
        """Handle search text changes in deleted services view"""
        self.refresh_deleted_view(search_text)
    
    # ==================== CRUD Operations ====================
    
    def add_service(self, service_data: dict):
        """Handle add service request"""
        try:
            print(f"Adding service: {service_data}")  # Debug log
            
            # Validate required fields
            if not service_data.get('name'):
                self.show_error("Service Name is required.")
                return
            if not service_data.get('price'):
                self.show_error("Service Price is required.")
                return
            if not service_data.get('duration'):
                self.show_error("Service Duration is required.")
                return
            
            # Validate price is positive number
            try:
                price = float(service_data['price'])
                if price <= 0:
                    self.show_error("Price must be greater than 0.")
                    return
            except ValueError:
                self.show_error("Price must be a valid number.")
                return
            
            # Validate duration is positive number
            try:
                duration = int(service_data['duration'])
                if duration <= 0:
                    self.show_error("Duration must be greater than 0.")
                    return
            except ValueError:
                self.show_error("Duration must be a valid number.")
                return
            
            # Check if service name already exists
            existing = ServiceModel.get_service_by_name(service_data['name'])
            if existing:
                self.show_error(f"Service '{service_data['name']}' already exists.")
                return
            
            # Create service
            service_id = ServiceModel.create_service({
                'name': service_data['name'],
                'price': price,
                'duration': duration,
                'status': service_data.get('status', 'Active')
            })
            
            if service_id:
                self.show_message("Success", f"Service '{service_data['name']}' added successfully!")
                self.refresh_service_view()
            else:
                self.show_error("Failed to add service. Please try again.")
                
        except Exception as e:
            print(f"Error in add_service: {e}")  # Debug log
            self.show_error(f"Error adding service: {str(e)}")
    
    def edit_service(self, service_data: dict):
        """Handle edit service request"""
        try:
            print(f"Editing service: {service_data}")  # Debug log
            
            service_id = service_data.get('id')
            if not service_id:
                self.show_error("Service ID is required.")
                return
            
            # Validate required fields
            if not service_data.get('name'):
                self.show_error("Service Name is required.")
                return
            if not service_data.get('price'):
                self.show_error("Service Price is required.")
                return
            if not service_data.get('duration'):
                self.show_error("Service Duration is required.")
                return
            
            # Validate price is positive number
            try:
                price = float(service_data['price'])
                if price <= 0:
                    self.show_error("Price must be greater than 0.")
                    return
            except ValueError:
                self.show_error("Price must be a valid number.")
                return
            
            # Validate duration is positive number
            try:
                duration = int(service_data['duration'])
                if duration <= 0:
                    self.show_error("Duration must be greater than 0.")
                    return
            except ValueError:
                self.show_error("Duration must be a valid number.")
                return
            
            # Convert service_id to int
            service_id_int = int(service_id)
            
            # Update service
            success = ServiceModel.update_service(service_id_int, {
                'name': service_data['name'],
                'price': price,
                'duration': duration,
                'status': service_data.get('status', 'Active')
            })
            
            if success:
                self.show_message("Success", f"Service '{service_data['name']}' updated successfully!")
                self.refresh_service_view()
            else:
                self.show_error("Failed to update service. Please try again.")
                
        except Exception as e:
            print(f"Error in edit_service: {e}")  # Debug log
            self.show_error(f"Error updating service: {str(e)}")
    
    def delete_service(self, service_id: str):
        """Handle delete service request (soft delete)"""
        try:
            print(f"Deleting service ID: {service_id}")  # Debug log
            
            # Convert service_id to int
            service_id_int = int(service_id)
            
            # Get service name for confirmation message
            service = ServiceModel.find(service_id_int)
            if not service:
                self.show_error("Service not found.")
                return
            
            success = ServiceModel.delete_service(service_id_int)
            
            if success:
                self.show_message("Success", f"Service '{service['name']}' has been moved to deleted services.")
                self.refresh_service_view()
            else:
                self.show_error("Failed to delete service. Please try again.")
                
        except Exception as e:
            print(f"Error in delete_service: {e}")  # Debug log
            self.show_error(f"Error deleting service: {str(e)}")
    
    def restore_service(self, service_data: dict):
        """Handle restore service request"""
        try:
            print(f"Restoring service: {service_data}")  # Debug log
            
            service_id = service_data.get('id')
            if not service_id:
                self.show_error("Service ID is required.")
                return
            
            # Convert service_id to int
            service_id_int = int(service_id)
            
            success = ServiceModel.restore_service(service_id_int)
            
            if success:
                self.show_message("Success", f"Service '{service_data['name']}' restored successfully!")
                # Refresh both views after restore
                self.refresh_service_view()
                self.refresh_deleted_view()
            else:
                self.show_error("Failed to restore service. Please try again.")
                
        except Exception as e:
            print(f"Error in restore_service: {e}")  # Debug log
            self.show_error(f"Error restoring service: {str(e)}")
    
    # ==================== View Management ====================
    
    def refresh_service_view(self):
        """Refresh the main service view with latest data and filters"""
        try:
            print(f"Refreshing service view with filter: {self.current_status_filter}, search: {self.current_search_text}")  # Debug log
            
            # Apply search and status filter
            if self.current_search_text:
                services = ServiceModel.search_services(self.current_search_text, self.current_status_filter)
            else:
                services = ServiceModel.get_all_with_details(self.current_status_filter)
            
            print(f"Loaded {len(services)} services")  # Debug log
            self.service_view.load_table(services)
            
        except Exception as e:
            print(f"Error in refresh_service_view: {e}")  # Debug log
            self.show_error(f"Error loading services: {str(e)}")
    
    def refresh_deleted_view(self, search_text: str = None):
        """Refresh the deleted services view with optional search"""
        try:
            if search_text is None:
                # Get current search text from view
                search_text = self.deleted_view.get_search_text()
            
            print(f"Refreshing deleted view with search: {search_text}")  # Debug log
            
            if search_text:
                deleted_services = ServiceModel.get_deleted_services(search_text)
            else:
                deleted_services = ServiceModel.get_deleted_services()
            
            print(f"Loaded {len(deleted_services)} deleted services")  # Debug log
            self.deleted_view.load_table(deleted_services)
            
        except Exception as e:
            print(f"Error in refresh_deleted_view: {e}")  # Debug log
            self.show_error(f"Error loading deleted services: {str(e)}")
    
    def show_service_view(self):
        """Show the main service view and hide deleted view"""
        print("Showing service view, hiding deleted view")  # Debug log
        self.refresh_service_view()
        self.deleted_view.hide()
        self.service_view.show()
        self.service_view.raise_()  # Bring to front
    
    def show_deleted_view(self):
        """Show the deleted services view"""
        print("Showing deleted view, hiding service view")  # Debug log
        self.refresh_deleted_view()
        self.service_view.hide()
        self.deleted_view.show()
        self.deleted_view.raise_()  # Bring to front
    
    def go_back(self):
        """Go back to main window and close all service views"""
        print("Going back to main dashboard")  # Debug log
        
        # Close both views
        if self.service_view:
            self.service_view.close()
        if self.deleted_view:
            self.deleted_view.close()
        
        # Show main window if it exists
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
        
        # Emit signal for any additional cleanup
        self.back_to_main_requested.emit()
    
    # ==================== Utility Methods ====================
    
    def show_message(self, title: str, message: str):
        """Show information message"""
        QMessageBox.information(self.service_view, title, message)
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.warning(self.service_view, "Error", message)
    
    def show_view(self):
        """Show the main service view (entry point)"""
        self.refresh_service_view()
        self.service_view.show()
    
    def close(self):
        """Close all views"""
        if self.service_view:
            self.service_view.close()
        if self.deleted_view:
            self.deleted_view.close()


# ==================== Test Entry Point ====================

def test_controller():
    """Test the service controller standalone"""
    app = QApplication(sys.argv)
    
    # Test database connection first
    try:
        from config.database import test_connection
        if not test_connection():
            print("❌ Database connection failed. Please check your MySQL configuration.")
            return
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return
    
    # Create and show controller
    controller = ServiceController()
    controller.show_view()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_controller()