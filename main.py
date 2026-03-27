"""
Hotel Management System - Main Application Entry Point
Initializes database connection and launches the main window with all modules
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox, QMainWindow, QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPixmap

from config.database import test_connection
from controllers.MainController import MainController


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(1000, 650)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Initialize main controller
        self.controller = MainController(central_widget)


class HotelManagementSystem:
    """Main application class that initializes all modules and shows the main window"""
    
    def __init__(self):
        print("🚀 Initializing application...")
        self.app = QApplication(sys.argv)
        
        # REMOVED: self.app.setStyle('Fusion') - this was overriding custom styles
        
        # Set application-wide font (this doesn't affect colors)
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        self.main_window = None
        self.splash = None
    
    def show_splash(self):
        """Show splash screen while loading"""
        print("💫 Showing splash screen...")
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(Qt.GlobalColor.darkGray)
        self.splash = QSplashScreen(splash_pixmap)
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
        
        try:
            # Create main window
            self.main_window = MainWindow()
            print("  ✅ Main window initialized!")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise e
    
    def show_main_interface(self):
        """Show the main application interface"""
        print("🖥️ Showing main interface...")
        
        # Close splash screen
        if self.splash:
            self.splash.close()
            self.splash = None
            print("  ✅ Splash screen closed")
        
        # Show main window
        if self.main_window:
            print("  📱 Showing main window...")
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            print(f"  ✅ Main window shown")
        else:
            print("  ❌ Main window is None!")
            self.show_error("Failed to initialize main window.")
    
    def show_error(self, message: str):
        """Show error message and exit"""
        print(f"❌ Error: {message}")
        
        if self.splash:
            self.splash.close()
        
        QMessageBox.critical(None, "Initialization Error", 
                            f"{message}\n\nPlease check your configuration and try again.")
        sys.exit(1)
    
    def run(self):
        """Run the application"""
        print("🏃 Running application...")
        
        # Show splash screen
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
            self.show_error(f"Error initializing modules: {str(e)}")
            return 1
        
        # Show main interface
        print("⏰ Showing main interface...")
        self.show_main_interface()
        
        print("🔄 Starting application event loop...")
        return self.app.exec()


def main():
    """Main entry point"""
    print("🌟 Hotel Management System Starting...")
    print("=" * 50)
    system = HotelManagementSystem()
    return system.run()


if __name__ == "__main__":
    sys.exit(main())