# MainFrame.py
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QTabWidget, QSizePolicy, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap

# Import from your views folder
from views.ReservationManagement.ReservationPanel import ReservationPanel
from views.ReservationManagement.GuestPanel import GuestPanelView
from views.ReservationManagement.ServicesPanel import ServicesPanel
from views.ReservationManagement.RoomPanel import RoomPanel

# Import database connection
from utils.db_connection import connect, disconnect, get_connection


# Helper to load and scale an image
def load_icon(relative_path: str, w: int, h: int) -> QPixmap:
    base = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base, relative_path)
    pixmap = QPixmap(full_path)
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(w, h,
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)


class MainFrameView(QWidget):
    def __init__(self, user_role: str = "Staff"):
        super().__init__()
        self.user_role = user_role
        self.db_connection = None
        
        self.setWindowTitle("Hotel Management System")
        self.setMinimumSize(1400, 800)
        self._build_ui()
        
        # Initialize database connection
        self._init_database()
        
        # Load icons after UI is built
        self._load_icons()
        
        # Initialize all panels
        self._init_panels()
    
    def _init_database(self):
        """Initialize database connection"""
        print("\n=== Initializing Database Connection ===")
        if connect():
            self.db_connection = get_connection()
            print("✓ Database connected successfully")
            
            # Test connection
            try:
                cursor = self.db_connection.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM guests")
                result = cursor.fetchone()
                cursor.close()
                print(f"✓ Found {result['count']} guests in database")
            except Exception as e:
                print(f"Warning: Could not query guests table: {e}")
        else:
            print("✗ Failed to connect to database")
            QMessageBox.warning(
                self, 
                "Database Connection Failed",
                "Could not connect to the database. Some features may not work properly."
            )
    
    def _load_icons(self):
        """Load icons for the header"""
        self.logo_label.setPixmap(load_icon("resources/admin_logo.jpg", 68, 68))
    
    def _init_panels(self):
        """Initialize all panel views"""
        try:
            print("\n=== Initializing Panels ===")
            
            # Pass database connection to panels that need it
            self.reservation_panel = ReservationPanel()
            self.guest_panel = GuestPanelView()
            self.services_panel = ServicesPanel()
            self.room_panel = RoomPanel()
            
            # Set database connection for panels that need it
            if hasattr(self.guest_panel, 'set_db_connection'):
                self.guest_panel.set_db_connection(self.db_connection)
            
            print("✓ All panels created successfully")
            
            # Add panels to tabs
            self.add_tab(self.reservation_panel, "RESERVATIONS")
            self.add_tab(self.guest_panel, "GUESTS")
            self.add_tab(self.services_panel, "SERVICES")
            self.add_tab(self.room_panel, "ROOMS")
            
            print("✓ Panels added to tabs")
            
        except Exception as e:
            print(f"Error initializing panels: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Initialization Error", f"Failed to load panels: {str(e)}")
    
    def _build_ui(self):
        """Build the main UI"""
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
        body.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(10, 10, 10, 0)
        body_layout.setSpacing(0)

        # ── TAB WIDGET ─────────────────────────────────────────────────────
        self.main_tabs = QTabWidget()
        self.main_tabs.setObjectName("main_tabs")
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
        """Build the header section"""
        header = QWidget()
        header.setObjectName("header")
        header.setStyleSheet("background-color: #FFE0E3; border: none;")
        header.setFixedHeight(75)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(68, 60)
        layout.addWidget(self.logo_label)

        title = QLabel("HOTEL MANAGEMENT SYSTEM")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038;")
        layout.addWidget(title)

        layout.addStretch()

        # Add user role label
        role_label = QLabel(f"Role: {self.user_role}")
        role_label.setFont(QFont("Segoe UI", 10))
        role_label.setStyleSheet("color: #2F2038; background-color: #FFE0E3; padding: 5px 10px; border-radius: 10px;")
        layout.addWidget(role_label)
        
        layout.addSpacing(20)

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

    def add_tab(self, widget: QWidget, title: str):
        """Add a tab to the main tab widget"""
        self.main_tabs.addTab(widget, title)
    
    def closeEvent(self, event):
        """Handle application close event"""
        print("\n=== Closing Application ===")
        disconnect()
        event.accept()


# ── RUNTIME ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create main window
    main_window = MainFrameView(user_role="Admin")
    main_window.show()
    
    sys.exit(app.exec())