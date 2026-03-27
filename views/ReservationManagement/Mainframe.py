import sys
import os

# Adjusting paths to ensure imports work from the current directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QTabWidget, QSizePolicy, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QPixmap

# ── FIXED IMPORTS ──────────────────────────────────────────────────────────
from views.ReservationManagement.ReservationPanel import ReservationPanel 
from views.ReservationManagement.GuestPanel import GuestPanelView
from views.ReservationManagement.RoomPanel import RoomPanel
from views.ReservationManagement.ServicesPanel import ServicesPanel


# ── Helper to load and scale an image ───────────────────────────────────────
def load_icon(relative_path: str, w: int, h: int) -> QPixmap:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    full_path = os.path.join(base, relative_path)
    pixmap = QPixmap(full_path)
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(w, h,
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)


class MainFrameView(QWidget):
    
    # Signal for controller communication
    back_requested = pyqtSignal()
    
    def __init__(self, user_role: str = "Staff", controller=None):
        super().__init__()
        self.user_role = user_role
        self.controller = controller
        self.setWindowTitle("Hotel Management System - Reservation")
        # FIX: Changed minimum size from 1400,800 to 1000,650 to match main window
        self.setMinimumSize(1000, 650)
        # FIX: Added size policy to allow proper expansion
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._load_icons()
        self._connect_signals()
        
        # Track if this view has been shown before
        self._has_been_shown = False

    def _load_icons(self):
        self.logo_label.setPixmap(load_icon("resources/admin_logo.jpg", 68, 68))

    def _build_ui(self):
        self.setObjectName("root")
        self.setStyleSheet("QWidget#root { background-color: #2F2038; border: none; }")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── HEADER ─────────────────────────────────────────────────────────
        root_layout.addWidget(self._build_header())

        # ── BODY ───────────────────────────────────────────────────────────
        body = QWidget()
        body.setObjectName("body")
        body.setStyleSheet("QWidget#body { background-color: #2F2038; border: none; }")
        # FIX: Added size policy to body widget
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(10, 10, 10, 0)
        body_layout.setSpacing(0)

        # ── TAB WIDGET ─────────────────────────────────────────────────────
        self.main_tabs = QTabWidget()
        self.main_tabs.setObjectName("main_tabs")
        # FIX: Added size policy to tab widget
        self.main_tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.main_tabs.setStyleSheet("""
            QTabWidget#main_tabs::pane {
                background-color: #3D2850;
                border: 1px solid #412B4E;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #412B4E;
                color: #A797A5;
                padding: 12px 30px;
                margin-right: 5px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #FFE0E3;
                color: #2F2038;
            }
            QTabBar::tab:hover:!selected {
                background-color: #5A3D6B;
                color: #FFE0E3;
            }
            QTableWidget::item:hover {
                background-color: #BE3455;
                color: #FFE0E3;
            }                         
        """)

        body_layout.addWidget(self.main_tabs, stretch=1)

        # ── FOOTER ────────────────────────────────────────────────────────
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setStyleSheet("background-color: #FFE0E3; border: none;")
        footer.setFixedHeight(30)
        body_layout.addSpacing(10)
        body_layout.addWidget(footer)

        root_layout.addWidget(body, stretch=1)

    def _build_header(self):
        header = QWidget()
        header.setObjectName("header")
        header.setStyleSheet("background-color: #FFE0E3; border: none;")
        header.setFixedHeight(75)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(68, 60)
        layout.addWidget(self.logo_label)

        title = QLabel("RESERVATION MANAGEMENT")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038;")
        layout.addWidget(title)

        layout.addStretch()

        self.back_btn = QPushButton("← BACK")
        self.back_btn.setFixedSize(110, 40)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: white;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        layout.addWidget(self.back_btn)

        return header

    def _connect_signals(self):
        """Connect internal signals"""
        self.back_btn.clicked.connect(self.handle_back)

    def handle_back(self):
        """Emit back signal to controller"""
        reply = QMessageBox.question(
            self,
            "Back to Dashboard",
            "Are you sure you want to go back? Any unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.back_requested.emit()

    def add_tab(self, widget: QWidget, title: str):
        """Add a tab to the main tab widget"""
        self.main_tabs.addTab(widget, title)

    def get_current_tab(self) -> int:
        """Get current tab index"""
        return self.main_tabs.currentIndex()

    def set_current_tab(self, index: int):
        """Set current tab by index"""
        self.main_tabs.setCurrentIndex(index)
    
    def showEvent(self, event):
        """Called when the widget is shown"""
        super().showEvent(event)
        # Refresh data when shown (if controller exists)
        if self.controller and hasattr(self.controller, 'refresh_all_data'):
            print("🔄 Mainframe shown, refreshing data...")
            self.controller.refresh_all_data()
        self._has_been_shown = True
    
    def hideEvent(self, event):
        """Called when the widget is hidden"""
        super().hideEvent(event)
        print("🔄 Mainframe hidden")

    def closeEvent(self, event):
        """Handle close event"""
        reply = QMessageBox.question(
            self,
            "Close",
            "Are you sure you want to close?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


# ── RUNTIME WITH CONTROLLER ────────────────────────────────────────────────
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from controllers.reservation_controller import ReservationController
    
    app = QApplication(sys.argv)
    
    # Test database connection first
    try:
        from config.database import test_connection
        if not test_connection():
            print("❌ Database connection failed. Please check your MySQL configuration.")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        sys.exit(1)
    
    # Create controller (this creates all views and handles logic)
    controller = ReservationController(user_role="Admin")
    
    # Show the main view
    controller.show_view()
    
    sys.exit(app.exec())