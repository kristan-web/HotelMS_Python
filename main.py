"""
Hotel Management System - Main Application Entry Point
Initializes database connection and launches the main window with all modules
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

from config.database import test_connection
from controllers.reservation_controller import ReservationController


class HotelManagementSystem:
    """Main application class that initializes all modules and shows the main window"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle('Fusion')
        
        # Set application-wide font
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        self.reservation_controller = None
        self.splash = None
    
    def show_splash(self):
        """Show splash screen while loading"""
        self.splash = QSplashScreen()
        self.splash.showMessage("Loading Hotel Management System...", 
                                Qt.AlignmentFlag.AlignCenter, 
                                Qt.GlobalColor.white)
        self.splash.show()
        self.app.processEvents()
    
    def check_database(self) -> bool:
        """Check database connection"""
        print("🔌 Checking database connection...")
        
        if test_connection():
            print("✅ Database connection successful!")
            return True
        else:
            print("❌ Database connection failed!")
            return False
    
    def init_modules(self):
        """Initialize all modules and controllers"""
        print("📦 Initializing modules...")
        
        # Initialize Reservation Controller (handles all reservation-related tabs)
        self.reservation_controller = ReservationController(user_role="Admin")
        
        print("✅ Reservation Controller initialized with all tabs!")
    
    def show_main_interface(self):
        """Show the main application interface"""
        if self.splash:
            self.splash.close()
        
        if self.reservation_controller:
            self.reservation_controller.show_view()
        else:
            self.show_error("Failed to initialize main window.")
    
    def show_error(self, message: str):
        """Show error message and exit"""
        if self.splash:
            self.splash.close()
        
        QMessageBox.critical(None, "Initialization Error", 
                            f"{message}\n\nPlease check your configuration and try again.")
        sys.exit(1)
    
    def run(self):
        """Run the application"""
        self.show_splash()
        
        # Check database connection
        if not self.check_database():
            self.show_error("Cannot connect to MySQL database.\n\n"
                          "Please ensure MySQL is running and credentials in config/database.py are correct.")
            return 1
        
        # Initialize modules
        try:
            self.init_modules()
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.show_error(f"Error initializing modules: {str(e)}")
            return 1
        
        # Show main interface after a short delay
        QTimer.singleShot(1000, self.show_main_interface)
        
        return self.app.exec()


def main():
    """Main entry point"""
    system = HotelManagementSystem()
    return system.run()


if __name__ == "__main__":
    sys.exit(main())