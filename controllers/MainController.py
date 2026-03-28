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


class MainController(QObject):
    """
    Main controller that manages application flow and view switching
    """
    
    def __init__(self, parent_widget=None):
        super().__init__()
        self.parent_widget = parent_widget
        self.account_controller = get_account_controller()
        self.current_user = None  # Store current user
        
        # Setup stacked widget for view management
        self.stacked_widget = QStackedWidget()
        
        # Views
        self.login_view = None
        self.registration_view = None
        self.dashboard_view = None
        
        # Controllers (persistent)
        self.reservation_controller = None
        self.service_controller = None
        
        # Track current view index
        self.LOGIN_INDEX = 0
        self.REGISTER_INDEX = 1
        self.DASHBOARD_INDEX = 2
        self.RESERVATION_INDEX = 3
        self.SERVICE_INDEX = 4
        
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
        
        # Create reservation controller (but not showing yet)
        self._init_reservation_controller()
        
        # Create service controller (but not showing yet)
        self._init_service_controller()
        
        # Add views to stacked widget in consistent order
        self.stacked_widget.addWidget(self.login_view)        # Index 0
        self.stacked_widget.addWidget(self.registration_view) # Index 1
        if self.dashboard_view:
            self.stacked_widget.addWidget(self.dashboard_view)  # Index 2
        
        # Add placeholder widgets for controllers (will be replaced when shown)
        self.reservation_placeholder = QWidget()
        self.service_placeholder = QWidget()
        self.stacked_widget.addWidget(self.reservation_placeholder)  # Index 3 - placeholder
        self.stacked_widget.addWidget(self.service_placeholder)      # Index 4 - placeholder
        
        # Set the stacked widget as the main widget
        if self.parent_widget:
            layout = QVBoxLayout(self.parent_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            layout.addWidget(self.stacked_widget)
            self.parent_widget.setLayout(layout)
        
        # Start with login view
        self.show_login()
    
    def _init_reservation_controller(self):
        """Initialize reservation controller (lazy loading)"""
        try:
            from controllers.reservation_controller import ReservationController
            
            # Create controller with parent reference
            self.reservation_controller = ReservationController(
                main_window=self.stacked_widget,
                user_role="Admin"
            )
            
            # Connect back signal
            if hasattr(self.reservation_controller, 'back_to_dashboard_requested'):
                self.reservation_controller.back_to_dashboard_requested.connect(self.show_dashboard)
            
            print("✅ Reservation controller initialized")
            
        except Exception as e:
            print(f"⚠️ Could not initialize reservation controller: {e}")
            import traceback
            traceback.print_exc()
            self.reservation_controller = None
    
    def _init_service_controller(self):
        """Initialize service controller (lazy loading)"""
        try:
            from controllers.service_controller import ServiceController
            
            # Create controller with parent reference
            self.service_controller = ServiceController(
                main_window=self.stacked_widget
            )
            
            # Connect back signal
            if hasattr(self.service_controller, 'back_to_main_requested'):
                self.service_controller.back_to_main_requested.connect(self.show_dashboard)
            
            # Connect switch signals to update stacked widget
            if hasattr(self.service_controller, 'switch_to_service_view'):
                self.service_controller.switch_to_service_view.connect(self._show_service_widget)
            if hasattr(self.service_controller, 'switch_to_deleted_view'):
                self.service_controller.switch_to_deleted_view.connect(self._show_deleted_widget)
            
            # Ensure the service view has a proper size
            if self.service_controller and self.service_controller.service_view:
                self.service_controller.service_view.setMinimumSize(900, 650)
            
            print("✅ Service controller initialized")
            
        except Exception as e:
            print(f"⚠️ Could not initialize service controller: {e}")
            import traceback
            traceback.print_exc()
            self.service_controller = None
    
    def _get_reservation_widget(self):
        """Get the actual reservation view widget"""
        if self.reservation_controller and hasattr(self.reservation_controller, 'mainframe'):
            return self.reservation_controller.mainframe
        return None
    
    def _get_service_widget(self):
        """Get the actual service view widget"""
        if self.service_controller and hasattr(self.service_controller, 'service_view'):
            return self.service_controller.service_view
        return None
    
    def _show_service_widget(self):
        """Show the service view widget in stacked widget"""
        if self.service_controller and self.service_controller.service_view:
            # Add to stack if not already
            if self.stacked_widget.indexOf(self.service_controller.service_view) == -1:
                self.stacked_widget.addWidget(self.service_controller.service_view)
            # Set current widget
            self.stacked_widget.setCurrentWidget(self.service_controller.service_view)
            self.stacked_widget.update()
            print("✅ Stacked widget showing service view")
    
    def _show_deleted_widget(self):
        """Show the deleted view widget in stacked widget"""
        if self.service_controller and self.service_controller.deleted_view:
            # Add to stack if not already
            if self.stacked_widget.indexOf(self.service_controller.deleted_view) == -1:
                self.stacked_widget.addWidget(self.service_controller.deleted_view)
            # Set current widget
            self.stacked_widget.setCurrentWidget(self.service_controller.deleted_view)
            self.stacked_widget.update()
            print("✅ Stacked widget showing deleted view")
    
    def _ensure_reservation_in_stack(self):
        """Ensure reservation view is in stacked widget"""
        reservation_widget = self._get_reservation_widget()
        if reservation_widget:
            if self.stacked_widget.indexOf(reservation_widget) == -1:
                self.stacked_widget.insertWidget(self.RESERVATION_INDEX, reservation_widget)
                print("✅ Reservation view added to stack")
            # Remove placeholder if exists
            if self.stacked_widget.widget(self.RESERVATION_INDEX + 1) == self.reservation_placeholder:
                self.stacked_widget.removeWidget(self.reservation_placeholder)
    
    def _ensure_service_in_stack(self):
        """Ensure service view is in stacked widget"""
        service_widget = self._get_service_widget()
        if service_widget:
            if self.stacked_widget.indexOf(service_widget) == -1:
                self.stacked_widget.insertWidget(self.SERVICE_INDEX, service_widget)
                print("✅ Service view added to stack")
            # Remove placeholder if exists
            if self.stacked_widget.widget(self.SERVICE_INDEX + 1) == self.service_placeholder:
                self.stacked_widget.removeWidget(self.service_placeholder)
    
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
            
            # Connect navigation cards using proper signals
            self.dashboard_view.reservation_clicked.connect(self.navigate_to_reservation)
            self.dashboard_view.service_clicked.connect(self.navigate_to_service)
        
        # Connect controller signals
        self.account_controller.login_successful.connect(self.on_login_success)
        self.account_controller.registration_successful.connect(self.on_registration_success)
        self.account_controller.login_failed.connect(self.on_login_failed)
        self.account_controller.registration_failed.connect(self.on_registration_failed)
    
    def handle_login(self, email: str, password: str):
        """Handle login request"""
        success, message, user_data = self.account_controller.login_admin(email, password)
    
    def handle_registration(self, user_data: dict):
        """Handle registration request"""
        success, message, user_id = self.account_controller.register_admin(user_data)
    
    def handle_staff_login(self):
        """Handle staff login button click"""
        self.login_view.show_message("Staff Login", "Staff login will be implemented soon.")
    
    def handle_forgot_password(self, source: str):
        """Handle forgot password request"""
        self.login_view.show_message("Forgot Password", "Password reset will be implemented soon.")
    
    def on_login_success(self, user_data: dict):
        """Called when login is successful"""
        self.current_user = user_data
        full_name = f"{user_data['first_name']} {user_data['last_name']}"
        print(f"✅ User logged in: {full_name}")

        QMessageBox.information(
            self.parent_widget,
            "Login Successful",
            f"Welcome back, {full_name}! 👋"
        )

        if self.dashboard_view:
            self.dashboard_view.set_session_label(full_name)
            self.load_dashboard_stats()

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
        self.stacked_widget.setCurrentIndex(self.LOGIN_INDEX)
        if self.parent_widget:
            self.parent_widget.setWindowTitle("Hotel Management System - Admin Login")
    
    def show_registration(self):
        """Switch to registration view"""
        self.stacked_widget.setCurrentIndex(self.REGISTER_INDEX)
        if self.parent_widget:
            self.parent_widget.setWindowTitle("Hotel Management System - Admin Registration")
    
    def show_dashboard(self):
        """Switch to dashboard view and refresh stats"""
        if self.dashboard_view:
            self.stacked_widget.setCurrentIndex(self.DASHBOARD_INDEX)
            if self.parent_widget:
                self.parent_widget.setWindowTitle("Hotel Management System - Admin Dashboard")
            self.load_dashboard_stats()
            print("🖥️ Showing dashboard")
        else:
            self.login_view.show_message("Info", "Dashboard view is not yet implemented.")
    
    def show_reservation(self):
        """Switch to reservation management view"""
        if self.reservation_controller:
            try:
                # Ensure reservation view is in stack
                self._ensure_reservation_in_stack()
                
                # Get the actual reservation widget
                reservation_widget = self._get_reservation_widget()
                
                if reservation_widget:
                    # Set minimum size
                    reservation_widget.setMinimumSize(1000, 700)
                    
                    # Show the view
                    self.stacked_widget.setCurrentIndex(self.RESERVATION_INDEX)
                    
                    # Force update
                    self.stacked_widget.update()
                    self.stacked_widget.repaint()
                    
                    if self.parent_widget:
                        self.parent_widget.setWindowTitle("Hotel Management System - Reservation Management")
                    
                    # Refresh data
                    self.reservation_controller.refresh_all_data()
                    print("🖥️ Showing reservation management")
                else:
                    print("❌ Reservation widget is None")
                    self.show_message("Error", "Reservation view is not available.")
                    
            except Exception as e:
                print(f"❌ Error showing reservation: {e}")
                import traceback
                traceback.print_exc()
                self.show_message("Error", "Could not open reservation management.")
        else:
            self.show_message("Error", "Reservation management is not available.")
    
    def show_service(self):
        """Switch to service management view"""
        if self.service_controller:
            try:
                # Ensure service view is visible in controller
                self.service_controller.show_service_view()
                self._show_service_widget()
                
                if self.parent_widget:
                    self.parent_widget.setWindowTitle("Hotel Management System - Service Management")
                
                print("🖥️ Showing service management")
            except Exception as e:
                print(f"❌ Error showing service: {e}")
                import traceback
                traceback.print_exc()
                self.show_message("Error", "Could not open service management.")
        else:
            self.show_message("Error", "Service management is not available.")
    
    def navigate_to_reservation(self):
        """Navigate to reservation management"""
        self.show_reservation()
    
    def navigate_to_service(self):
        """Navigate to service management"""
        self.show_service()
    
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
            
            # Reset controllers to ensure clean state on next login
            if self.reservation_controller:
                self.reservation_controller.close()
            
            if self.service_controller:
                self.service_controller.close()
            
            self.show_login()
            print("✅ User logged out")
    
    def get_current_user_id(self) -> int:
        """Get current logged-in user ID"""
        if self.current_user and 'id' in self.current_user:
            return self.current_user['id']
        return 1  # Default to admin ID 1 if not found
    
    def load_dashboard_stats(self):
        """Load statistics from database to update dashboard"""
        try:
            from models.reservation_model import ReservationModel
            from models.service_model import ServiceModel
            from models.user_model import UserModel
            
            # Get reservation statistics
            reservation_stats = ReservationModel.get_stats()
            total_reservations = reservation_stats.get('total_reservations', 0)
            if self.dashboard_view:
                self.dashboard_view.set_total_reservations(total_reservations)
            print(f"📊 Total reservations: {total_reservations}")
            
            # Get active services count
            active_services = ServiceModel.count_active_services()
            if self.dashboard_view:
                self.dashboard_view.set_available_services(active_services)
            print(f"📊 Active services: {active_services}")
            
            # Get total staff count
            total_staff = UserModel.count_staff()
            if self.dashboard_view:
                self.dashboard_view.set_total_staff(total_staff)
            print(f"📊 Total staff: {total_staff}")
            
            # Get total revenue from completed reservations
            total_revenue = ReservationModel.get_total_revenue()
            if self.dashboard_view:
                self.dashboard_view.set_total_revenue(int(total_revenue))
            print(f"📊 Total revenue: ₱{total_revenue:,.2f}")
            
        except Exception as e:
            print(f"⚠️ Error loading dashboard stats: {e}")
            import traceback
            traceback.print_exc()
            # Set default values on error
            if self.dashboard_view:
                self.dashboard_view.set_total_reservations(0)
                self.dashboard_view.set_available_services(0)
                self.dashboard_view.set_total_staff(0)
                self.dashboard_view.set_total_revenue(0)
    
    def show_message(self, title: str, message: str):
        """Show a message box"""
        QMessageBox.information(self.parent_widget, title, message)
    
    def get_current_view(self):
        """Get the currently active view"""
        return self.stacked_widget.currentWidget()