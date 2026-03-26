"""
Main Controller - Manages application flow and view switching
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

from controllers.AccountController import get_account_controller
from views.AccountManagement.AccountCreation.AdminLoginView import AdminLoginView
from views.AccountManagement.AccountCreation.AdminRegistrationView import AdminRegistrationView
from views.Dashboard.AdminDashboardView import AdminDashboardView
from views.ReservationManagement.Mainframe import MainFrameView
from views.ServiceManagement.ServiceView import ServiceView  # Import ServiceView


class MainController(QObject):
    """
    Main controller that manages application flow and view switching
    """
    
    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self.account_controller = get_account_controller()
        
        # Setup stacked widget for view management
        self.stacked_widget = QStackedWidget()
        
        # Create views
        self.login_view = None
        self.registration_view = None
        self.dashboard_view = None
        self.reservation_view = None
        self.service_view = None
        
        # Current user data
        self.current_user = None
        
        # Initialize
        self.setup_views()
        self.connect_signals()
        
    def setup_views(self):
        """Create and setup all views"""
        # Create login view
        self.login_view = AdminLoginView()
        
        # Create registration view
        self.registration_view = AdminRegistrationView()
        
        # Create dashboard view
        try:
            self.dashboard_view = AdminDashboardView()
            print("✅ Dashboard view created successfully")
        except Exception as e:
            print(f"⚠️ Could not create dashboard view: {e}")
            self.dashboard_view = None
        
        # Create reservation management view
        try:
            self.reservation_view = MainFrameView(user_role="Admin", controller=self)
            print("✅ Reservation view created successfully")
            self.setup_reservation_tabs()
        except Exception as e:
            print(f"⚠️ Could not create reservation view: {e}")
            import traceback
            traceback.print_exc()
            self.reservation_view = None
        
        # Create service management view
        try:
            self.service_view = ServiceView()
            print("✅ Service view created successfully")
        except Exception as e:
            print(f"⚠️ Could not create service view: {e}")
            import traceback
            traceback.print_exc()
            self.service_view = None
        
        # Add views to stacked widget
        self.stacked_widget.addWidget(self.login_view)  # Index 0
        self.stacked_widget.addWidget(self.registration_view)  # Index 1
        if self.dashboard_view:
            self.stacked_widget.addWidget(self.dashboard_view)  # Index 2
        if self.reservation_view:
            self.stacked_widget.addWidget(self.reservation_view)  # Index 3
        if self.service_view:
            self.stacked_widget.addWidget(self.service_view)  # Index 4
        
        # Set the stacked widget as the main widget
        if self.parent_widget:
            layout = QVBoxLayout(self.parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.stacked_widget)
            self.parent_widget.setLayout(layout)
        
        # Start with login view
        self.show_login()
    
    def setup_reservation_tabs(self):
        """Setup tabs in reservation view"""
        if not self.reservation_view:
            return
        
        try:
            from views.ReservationManagement.ReservationPanel import ReservationPanel
            from views.ReservationManagement.GuestPanel import GuestPanelView
            from views.ReservationManagement.RoomPanel import RoomPanel
            from views.ReservationManagement.ServicesPanel import ServicesPanel
            
            reservation_panel = ReservationPanel()
            guest_panel = GuestPanelView()
            room_panel = RoomPanel()
            services_panel = ServicesPanel()
            
            self.reservation_view.add_tab(reservation_panel, "RESERVATIONS")
            self.reservation_view.add_tab(guest_panel, "GUESTS")
            self.reservation_view.add_tab(room_panel, "ROOMS")
            self.reservation_view.add_tab(services_panel, "SERVICES")
            
            print("✅ Reservation tabs added successfully")
        except Exception as e:
            print(f"⚠️ Could not add tabs to reservation view: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_service_connections(self):
        """Setup service view connections and load initial data"""
        if not self.service_view:
            return
        
        try:
            # Connect service view signals
            self.service_view.back_requested.connect(self.show_dashboard)
            self.service_view.add_requested.connect(self.handle_add_service)
            self.service_view.edit_requested.connect(self.handle_edit_service)
            self.service_view.delete_requested.connect(self.handle_delete_service)
            self.service_view.filter_changed.connect(self.handle_service_filter)
            self.service_view.search_changed.connect(self.handle_service_search)
            self.service_view.show_deleted_requested.connect(self.handle_show_deleted_services)
            
            # Load initial service data
            self.load_service_data()
            
            print("✅ Service view connections established")
        except Exception as e:
            print(f"⚠️ Could not setup service connections: {e}")
    
    def connect_signals(self):
        """Connect all signals between views and controller"""
        
        # Connect login view signals
        self.login_view.login_requested.connect(self.handle_login)
        self.login_view.staff_login_requested.connect(self.handle_staff_login)
        self.login_view.forgot_password_requested.connect(self.handle_forgot_password)
        self.login_view.register_requested.connect(self.show_registration)
        
        # Connect registration view signals
        self.registration_view.registration_requested.connect(self.handle_registration)
        self.registration_view.back_requested.connect(self.show_login)
        
        # Connect dashboard signals if dashboard exists
        if self.dashboard_view:
            self.dashboard_view.logout_btn.clicked.connect(self.handle_logout)
            
            # Connect navigation cards
            if hasattr(self.dashboard_view, 'reservation_card'):
                self.dashboard_view.reservation_card.mousePressEvent = lambda e: self.navigate_to_reservation()
            if hasattr(self.dashboard_view, 'service_card'):
                self.dashboard_view.service_card.mousePressEvent = lambda e: self.navigate_to_service()
        
        # Connect reservation view signals if reservation view exists
        if self.reservation_view:
            if hasattr(self.reservation_view, 'back_requested'):
                self.reservation_view.back_requested.connect(self.show_dashboard)
        
        # Connect service view signals
        if self.service_view:
            self.setup_service_connections()
        
        # Connect controller signals
        self.account_controller.login_successful.connect(self.on_login_success)
        self.account_controller.registration_successful.connect(self.on_registration_success)
        self.account_controller.login_failed.connect(self.on_login_failed)
        self.account_controller.registration_failed.connect(self.on_registration_failed)
    
    def load_service_data(self):
        """Load service data from database"""
        from config.database import get_connection
        
        conn = get_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            query = "SELECT id, name, price, duration, status FROM services WHERE is_deleted = 0"
            cursor.execute(query)
            services = cursor.fetchall()
            
            # Convert to list of dicts
            service_list = []
            for s in services:
                service_list.append({
                    'id': s[0],
                    'name': s[1],
                    'price': s[2],
                    'duration': s[3],
                    'status': s[4]
                })
            
            if self.service_view:
                self.service_view.load_table(service_list)
            
            print(f"✅ Loaded {len(service_list)} services")
        except Exception as e:
            print(f"⚠️ Error loading services: {e}")
        finally:
            conn.close()
    
    def handle_add_service(self, service_data):
        """Handle adding a new service"""
        from config.database import get_connection
        
        conn = get_connection()
        if not conn:
            self.service_view.show_message("Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO services (name, price, duration, status, is_deleted, created_at)
                VALUES (%s, %s, %s, %s, 0, NOW())
            """
            cursor.execute(query, (
                service_data['name'],
                service_data['price'],
                service_data['duration'],
                service_data['status']
            ))
            conn.commit()
            
            self.service_view.show_message("Success", "Service added successfully")
            self.load_service_data()  # Refresh the table
            
        except Exception as e:
            conn.rollback()
            print(f"Error adding service: {e}")
            self.service_view.show_message("Error", f"Failed to add service: {str(e)}")
        finally:
            conn.close()
    
    def handle_edit_service(self, service_data):
        """Handle editing a service"""
        from config.database import get_connection
        
        conn = get_connection()
        if not conn:
            self.service_view.show_message("Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            query = """
                UPDATE services 
                SET name = %s, price = %s, duration = %s, status = %s, updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (
                service_data['name'],
                service_data['price'],
                service_data['duration'],
                service_data['status'],
                service_data['id']
            ))
            conn.commit()
            
            self.service_view.show_message("Success", "Service updated successfully")
            self.load_service_data()  # Refresh the table
            
        except Exception as e:
            conn.rollback()
            print(f"Error updating service: {e}")
            self.service_view.show_message("Error", f"Failed to update service: {str(e)}")
        finally:
            conn.close()
    
    def handle_delete_service(self, service_id):
        """Handle deleting a service (soft delete)"""
        from config.database import get_connection
        
        conn = get_connection()
        if not conn:
            self.service_view.show_message("Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            query = "UPDATE services SET is_deleted = 1, deleted_at = NOW() WHERE id = %s"
            cursor.execute(query, (service_id,))
            conn.commit()
            
            self.service_view.show_message("Success", "Service deleted successfully")
            self.load_service_data()  # Refresh the table
            self.load_dashboard_stats()  # Update dashboard stats
            
        except Exception as e:
            conn.rollback()
            print(f"Error deleting service: {e}")
            self.service_view.show_message("Error", f"Failed to delete service: {str(e)}")
        finally:
            conn.close()
    
    def handle_service_filter(self, status):
        """Handle service status filter"""
        # Implement filtering logic
        pass
    
    def handle_service_search(self, search_text):
        """Handle service search"""
        # Implement search logic
        pass
    
    def handle_show_deleted_services(self):
        """Handle showing deleted services"""
        # Implement show deleted services
        pass
    
    def handle_login(self, email: str, password: str):
        """Handle login request"""
        success, message, user_data = self.account_controller.login_admin(email, password)
        
        if not success:
            pass
            
    def handle_registration(self, user_data: dict):
        """Handle registration request"""
        success, message, user_id = self.account_controller.register_admin(user_data)
        
        if not success:
            pass
            
    def handle_staff_login(self):
        """Handle staff login button click"""
        self.login_view.show_message("Staff Login", "Staff login will be implemented soon.")
    
    def handle_forgot_password(self, source: str):
        """Handle forgot password request"""
        self.login_view.show_message("Forgot Password", "Password reset will be implemented soon.")
    
    def on_login_success(self, user_data: dict):
        """Called when login is successful"""
        self.current_user = user_data
        print(f"✅ User logged in: {user_data['first_name']} {user_data['last_name']}")
        
        if self.dashboard_view:
            full_name = f"{user_data['first_name']} {user_data['last_name']}"
            self.dashboard_view.set_session_label(full_name)
            self.load_dashboard_stats()
        
        if self.reservation_view and hasattr(self.reservation_view, 'user_role'):
            self.reservation_view.user_role = "Admin"
        
        self.show_dashboard()
        
    def on_login_failed(self, error_msg: str):
        """Called when login fails"""
        self.login_view.show_error(error_msg)
        
    def on_registration_success(self, email: str):
        """Called when registration is successful"""
        self.registration_view.show_message(
            "Registration Successful", 
            f"Account created successfully for {email}!\nPlease login."
        )
        self.show_login()
        
    def on_registration_failed(self, error_msg: str):
        """Called when registration fails"""
        self.registration_view.show_error(error_msg)
        
    def show_login(self):
        """Switch to login view"""
        self.stacked_widget.setCurrentIndex(0)
        if self.parent_widget:
            self.parent_widget.setWindowTitle("Hotel Management System - Admin Login")
        
    def show_registration(self):
        """Switch to registration view"""
        self.stacked_widget.setCurrentIndex(1)
        if self.parent_widget:
            self.parent_widget.setWindowTitle("Hotel Management System - Admin Registration")
    
    def show_dashboard(self):
        """Switch to dashboard view"""
        if self.dashboard_view:
            self.stacked_widget.setCurrentIndex(2)
            if self.parent_widget:
                self.parent_widget.setWindowTitle("Hotel Management System - Admin Dashboard")
            self.load_dashboard_stats()
        else:
            self.login_view.show_message("Info", "Dashboard view is not yet implemented.")
    
    def show_reservation(self):
        """Switch to reservation management view"""
        if self.reservation_view:
            self.stacked_widget.setCurrentIndex(3)
            if self.parent_widget:
                self.parent_widget.setWindowTitle("Hotel Management System - Reservation Management")
            self.refresh_reservation_data()
        else:
            self.show_message("Error", "Reservation management is not available.")
    
    def show_service(self):
        """Switch to service management view"""
        if self.service_view:
            self.stacked_widget.setCurrentIndex(4)
            if self.parent_widget:
                self.parent_widget.setWindowTitle("Hotel Management System - Service Management")
            self.load_service_data()  # Refresh service data
        else:
            self.show_message("Error", "Service management is not available.")
    
    def refresh_reservation_data(self):
        """Refresh data in reservation view"""
        if not self.reservation_view:
            return
        
        try:
            for i in range(self.reservation_view.main_tabs.count()):
                tab = self.reservation_view.main_tabs.widget(i)
                if hasattr(tab, 'refresh_data'):
                    tab.refresh_data()
            print("✅ Reservation data refreshed")
        except Exception as e:
            print(f"⚠️ Could not refresh reservation data: {e}")
    
    def handle_logout(self):
        """Handle logout request"""
        reply = QMessageBox.question(
            self.login_view,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_user = None
            if self.login_view:
                self.login_view.password_input.clear()
            self.show_login()
            print("✅ User logged out")
    
    def navigate_to_reservation(self):
        """Navigate to reservation management"""
        self.show_reservation()
    
    def navigate_to_service(self):
        """Navigate to service management"""
        self.show_service()
    
    def load_dashboard_stats(self):
        """Load statistics from database to update dashboard"""
        from config.database import get_connection
        
        conn = get_connection()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM reservations WHERE status != 'Cancelled'")
            total_reservations = cursor.fetchone()[0]
            self.dashboard_view.set_total_reservations(total_reservations)
            
            cursor.execute("SELECT COUNT(*) FROM services WHERE is_deleted = 0 AND status = 'Active'")
            available_services = cursor.fetchone()[0]
            self.dashboard_view.set_available_services(available_services)
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Staff' AND is_deleted = 0")
            total_staff = cursor.fetchone()[0]
            self.dashboard_view.set_total_staff(total_staff)
            
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM reservations WHERE status = 'Completed'")
            total_revenue = cursor.fetchone()[0]
            self.dashboard_view.set_total_revenue(int(total_revenue))
            
            print("✅ Dashboard statistics loaded")
            
        except Exception as e:
            print(f"⚠️ Error loading dashboard stats: {e}")
            self.dashboard_view.set_total_reservations(0)
            self.dashboard_view.set_available_services(0)
            self.dashboard_view.set_total_staff(0)
            self.dashboard_view.set_total_revenue(0)
        finally:
            conn.close()
    
    def show_message(self, title: str, message: str):
        """Show a message box"""
        QMessageBox.information(self.parent_widget, title, message)
    
    def get_current_view(self):
        """Get the currently active view"""
        return self.stacked_widget.currentWidget()