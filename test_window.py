# test_window.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import QApplication
from views.AccountManagement.AccountCreation.AdminLoginView import AdminLoginView

print("Starting application...")
app = QApplication(sys.argv)

print("Creating login view...")
window = AdminLoginView()
window.setWindowTitle("Admin Login Test")
window.resize(1000, 650)

print("Showing window...")
window.show()

print("Window should be visible now")
print("Entering event loop...")
sys.exit(app.exec())