import sys
import os

# Adjusting paths to ensure imports work from the current directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QTabWidget, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap

# ── FIXED IMPORTS ──────────────────────────────────────────────────────────
# Matching the names exactly as they appear in your .py files
from ReservationPanel import ReservationPanel 
from GuestPanel import GuestPanelView
from ServicesPanel import ServicesPanel
from RoomPanel import RoomPanel


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
    def __init__(self, user_role: str = "Staff"):
        super().__init__()
        self.user_role = user_role
        self.setWindowTitle("Hotel Management System - Reservation")
        self.setMinimumSize(1400, 800)
        self._build_ui()
        self._load_icons()

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

    def add_tab(self, widget: QWidget, title: str):
        self.main_tabs.addTab(widget, title)


# ── RUNTIME ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    main_window = MainFrameView(user_role="Admin")

    try:
        # Initializing classes with their CORRECT names
        res_view = ReservationPanel()  # Fixed name
        guest_view = GuestPanelView()  # Fixed name
        service_view = ServicesPanel()
        room_view = RoomPanel() 

        # Add to Tabs
        main_window.add_tab(res_view, "RESERVATIONS")
        main_window.add_tab(guest_view, "GUESTS")
        main_window.add_tab(service_view, "SERVICES")
        main_window.add_tab(room_view, "ROOMS")

    except Exception as e:
        print(f"Error starting panels: {e}")
        sys.exit(1)

    main_window.show()
    sys.exit(app.exec())