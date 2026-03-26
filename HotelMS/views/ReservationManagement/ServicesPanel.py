# views/ServiceManagement/ServicesPanel.py (MODIFIED)
import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QComboBox, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from controllers.service_controller import get_service_controller


class ServicesPanel(QWidget):
    """Service booking panel with real service data from database."""
    
    def __init__(self):
        super().__init__()
        
        # Match the expanding policy
        self.setSizePolicy(self.sizePolicy().Policy.Expanding, self.sizePolicy().Policy.Expanding)
        
        # Get service controller
        self.service_controller = get_service_controller()
        
        # Color Palette
        self.BG_ROOT = "#2F2038"      
        self.BG_CARD = "#3D2850"      
        self.BORDER_COLOR = "#412B4E" 
        self.TEXT_LAVENDER = "#FFE0E3" 
        self.ACCENT_CRIMSON = "#BE3455" 
        self.INPUT_BG = "#F9F5FF"     

        # Store selected service price for calculation
        self.current_service_price = 0.0
        
        # Static guest data (should be replaced with GuestController later)
        self.guests = ["John Doe", "Jane Smith", "Guest 3"]
        
        # Static booking data (should be replaced with ReservationController later)
        self.static_bookings = [
            {"id": "1", "guest": "John Doe", "service": "Spa Massage", "time": "2024-05-20 14:00", "dur": "60 mins", "total": "1500.00", "stat": "COMPLETED"},
            {"id": "2", "guest": "Jane Smith", "service": "Gym Session", "time": "2024-05-21 09:00", "dur": "120 mins", "total": "500.00", "stat": "PENDING"},
        ]

        self.init_ui()
        self.load_services()
        self.load_data()

    def init_ui(self):
        self.setObjectName("service_root")
        self.setStyleSheet(f"QWidget#service_root {{ background-color: {self.BG_ROOT}; border: none; }}")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ── TOP FORM PANEL (Triple Card Layout) ───────────────────────────
        main_layout.addWidget(self._build_booking_panel())

        # ── BOTTOM TABLE PANEL (Management Section) ───────────────────────
        main_layout.addWidget(self._build_table_panel(), stretch=1)

    def _build_booking_panel(self):
        form_outer = QFrame()
        form_outer.setObjectName("form_outer")
        form_outer.setStyleSheet(f"""
            QFrame#form_outer {{
                background-color: {self.BG_ROOT};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 6px;
            }}
        """)

        layout = QHBoxLayout(form_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Sub-panel 1: Selection
        p1 = self._create_sub_panel()
        lay1 = QVBoxLayout(p1)
        lay1.addWidget(self._styled_label("Guest Name:"))
        self.combo_guest = self._styled_combo(self.guests)
        lay1.addWidget(self.combo_guest)
        lay1.addWidget(self._styled_label("Service Type:"))
        self.combo_service = self._styled_combo([])  # Will be populated
        self.combo_service.currentIndexChanged.connect(self.on_service_selected)
        lay1.addWidget(self.combo_service)
        layout.addWidget(p1, stretch=1)

        # Sub-panel 2: Duration
        p2 = self._create_sub_panel()
        lay2 = QVBoxLayout(p2)
        lay2.addWidget(self._styled_label("Duration (mins):"))
        self.txt_duration = self._styled_input("60")
        self.txt_duration.textChanged.connect(self.update_total_price)
        lay2.addWidget(self.txt_duration)
        lay2.addStretch()
        layout.addWidget(p2, stretch=1)

        # Sub-panel 3: Confirmation
        p3 = self._create_sub_panel()
        lay3 = QVBoxLayout(p3)
        self.lbl_total = QLabel("Total: ₱0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setStyleSheet(f"color: {self.TEXT_LAVENDER}; font-size: 16pt; font-weight: bold; margin-bottom: 5px;")
        
        self.btn_book = self._action_button("BOOK NOW", self.ACCENT_CRIMSON)
        self.btn_book.setFixedWidth(200)
        self.btn_book.clicked.connect(self.handle_book)
        
        lay3.addWidget(self.lbl_total)
        lay3.addWidget(self.btn_book, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(p3, stretch=1)

        return form_outer

    def _build_table_panel(self):
        table_outer = QFrame()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet(f"QFrame#table_outer {{ background-color: {self.BG_ROOT}; border: 1px solid {self.BORDER_COLOR}; border-radius: 6px; }}")
        
        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)

        # Table Toolbar
        tools = QHBoxLayout()
        self.btn_refresh = self._action_button("REFRESH", "#412B4E")
        self.btn_delete = self._action_button("DELETE", self.ACCENT_CRIMSON)
        
        self.btn_refresh.clicked.connect(self.load_data)
        self.btn_delete.clicked.connect(self.handle_delete)
        
        tools.addWidget(self.btn_refresh)
        tools.addWidget(self.btn_delete)
        tools.addStretch()
        layout.addLayout(tools)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Guest", "Service", "Scheduled", "Duration", "Total", "Status"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.BG_CARD}; color: #F2F2F2;
                gridline-color: {self.BORDER_COLOR}; border-radius: 4px; border: none;
            }}
            QHeaderView::section {{
                background-color: {self.BORDER_COLOR}; color: {self.TEXT_LAVENDER};
                font-weight: bold; border: none; padding: 6px;
            }}
            QTableWidget::item:selected {{ background-color: {self.ACCENT_CRIMSON}; color: {self.TEXT_LAVENDER}; }}
        """)
        
        layout.addWidget(self.table)
        return table_outer

    # --- UI Helpers ---
    def _create_sub_panel(self):
        p = QFrame()
        p.setStyleSheet(f"background-color: {self.BG_CARD}; border-radius: 6px;")
        return p

    def _styled_label(self, t):
        l = QLabel(t)
        l.setStyleSheet(f"color: {self.TEXT_LAVENDER}; background: transparent; font-size: 11pt;")
        l.setFont(QFont("Segoe UI Semilight", 11))
        return l

    def _styled_input(self, text=""):
        e = QLineEdit(text)
        e.setFixedHeight(35)
        e.setStyleSheet(f"background-color: {self.INPUT_BG}; color: #2F2038; border-radius: 4px; padding-left: 10px;")
        return e

    def _styled_combo(self, items):
        c = QComboBox()
        if items:
            c.addItems(items)
        c.setFixedHeight(35)
        c.setStyleSheet(f"background-color: {self.INPUT_BG}; color: #2F2038; border-radius: 4px; padding-left: 5px;")
        return c

    def _action_button(self, t, color):
        b = QPushButton(t)
        b.setFixedSize(110, 34)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        b.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: #FFE0E3;
                border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        return b

    # --- Service Loading ---
    def load_services(self):
        """Load active services from database into dropdown."""
        services = self.service_controller.get_all_active()
        
        # Clear and repopulate combo box
        self.combo_service.clear()
        for service in services:
            self.combo_service.addItem(f"{service['name']} - ₱{service['price']:.2f}", service)
        
        # Set default service
        if services:
            self.combo_service.setCurrentIndex(0)
            self.on_service_selected(0)
    
    def on_service_selected(self, index):
        """Handle service selection change."""
        if index >= 0:
            service_data = self.combo_service.itemData(index)
            if service_data:
                self.current_service_price = service_data['price']
                # Auto-fill duration from selected service
                self.txt_duration.setText(str(service_data['duration']))
                self.update_total_price()
    
    def update_total_price(self):
        """Calculate and update total price based on service price and duration."""
        try:
            duration = int(self.txt_duration.text() or 0)
            # Assuming price is per minute? If price is fixed per session, adjust calculation
            # For now, assuming price is per session regardless of duration
            # If price is per hour/minute, use: total = (self.current_service_price / 60) * duration
            total = self.current_service_price  # Fixed price per service
            self.lbl_total.setText(f"Total: ₱{total:.2f}")
        except ValueError:
            self.lbl_total.setText("Total: ₱0.00")
    
    # --- Booking Logic ---
    def handle_book(self):
        """Handle book button click."""
        if self.combo_service.currentIndex() < 0:
            QMessageBox.warning(self, "No Service", "Please select a service to book.")
            return
        
        service_data = self.combo_service.itemData(self.combo_service.currentIndex())
        
        new_entry = {
            "id": str(len(self.static_bookings) + 1),
            "guest": self.combo_guest.currentText(),
            "service": service_data['name'],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "dur": f"{self.txt_duration.text()} mins",
            "total": f"{self.current_service_price:.2f}",
            "stat": "PENDING"
        }
        self.static_bookings.append(new_entry)
        self.load_data()
        QMessageBox.information(self, "Success", f"Service '{service_data['name']}' booked successfully!")
    
    def load_data(self):
        """Load bookings into table."""
        self.table.setRowCount(0)
        for b in self.static_bookings:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(b["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(b["guest"]))
            self.table.setItem(row, 2, QTableWidgetItem(b["service"]))
            self.table.setItem(row, 3, QTableWidgetItem(b["time"]))
            self.table.setItem(row, 4, QTableWidgetItem(b["dur"]))
            self.table.setItem(row, 5, QTableWidgetItem(b["total"]))
            self.table.setItem(row, 6, QTableWidgetItem(b["stat"]))

    def handle_delete(self):
        """Handle delete button click."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a booking to delete.")
            return
        self.static_bookings.pop(selected[0].row())
        self.load_data()
        QMessageBox.information(self, "Success", "Booking deleted successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServicesPanel()
    window.resize(1100, 750)
    window.show()
    sys.exit(app.exec())