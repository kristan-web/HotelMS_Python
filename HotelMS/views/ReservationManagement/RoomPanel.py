# views/ReservationManagement/RoomPanel.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, 
    QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSizePolicy, QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

# Import controller
from controllers.room_controller import RoomController
from utils.db_connection import get_connection


class RoomPanel(QWidget):
    def __init__(self): 
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self._build_ui()
        self._setup_controller()
    
    def _setup_controller(self):
        """Setup the controller with database connection"""
        try:
            db_connection = get_connection()
            if db_connection:
                self.controller = RoomController(db_connection)
                self.controller.set_view(self)
                print("✓ Room controller initialized")
            else:
                print("✗ Could not get database connection for room panel")
                # Load static data as fallback
                self.load_static_rooms()
        except Exception as e:
            print(f"Error setting up room controller: {e}")
            self.load_static_rooms()
    
    def load_static_rooms(self):
        """Load static data as fallback"""
        static_rooms = [
            {"id": "1", "num": "101", "type": "SINGLE", "price": "1500.00", "cap": "1", "stat": "AVAILABLE", "desc": "Standard Single"},
            {"id": "2", "num": "202", "type": "DELUXE", "price": "3500.00", "cap": "2", "stat": "OCCUPIED", "desc": "Seaside View"},
        ]
        self.load_rooms(static_rooms)

    def _build_ui(self):
        self.setObjectName("room_root")
        self.setStyleSheet("QWidget#room_root { background-color: #2F2038; border: none; }")
        
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # ── TOP FORM PANEL ───────────────────────────────────────────────
        root_layout.addWidget(self._build_form_panel())
        
        # ── BOTTOM TABLE PANEL ───────────────────────────────────────────
        root_layout.addWidget(self._build_table_panel(), stretch=1)

    def _build_form_panel(self):
        form_outer = QFrame()
        form_outer.setObjectName("form_outer")
        form_outer.setStyleSheet("""
            QFrame#form_outer {
                background-color: #2F2038;
                border: 1px solid #412B4E;
                border-radius: 6px;
            }
        """)
        layout = QHBoxLayout(form_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Panel 1: Basic Info
        p1 = self._create_sub_panel()
        lay1 = QVBoxLayout(p1)
        lay1.addWidget(self._styled_label("Room Number:"))
        self.room_number_field = self._styled_input()
        lay1.addWidget(self.room_number_field)
        lay1.addWidget(self._styled_label("Capacity:"))
        self.capacity_field = self._styled_input()
        lay1.addWidget(self.capacity_field)
        layout.addWidget(p1, stretch=1)

        # Panel 2: Pricing & Type
        p2 = self._create_sub_panel()
        lay2 = QVBoxLayout(p2)
        lay2.addWidget(self._styled_label("Room Type:"))
        self.room_type_combo = QComboBox()
        self.room_type_combo.addItems(["SINGLE", "DOUBLE", "DELUXE", "SUITE"])
        self.room_type_combo.setFixedHeight(35)
        self.room_type_combo.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px; padding-left: 8px;")
        lay2.addWidget(self.room_type_combo)
        lay2.addWidget(self._styled_label("Price per Night:"))
        self.price_field = self._styled_input()
        lay2.addWidget(self.price_field)
        layout.addWidget(p2, stretch=1)

        # Panel 3: Description & Add Action
        p3 = self._create_sub_panel()
        lay3 = QVBoxLayout(p3)
        lay3.addWidget(self._styled_label("Description / Notes:"))
        self.description_field = self._styled_input()
        lay3.addWidget(self.description_field)
        
        lay3.addStretch()
        self.btn_add = self._action_button("Add Room", "#BE3455")
        self.btn_clear = self._action_button("Clear Form", "#412B4E")
        self.btn_add.setFixedWidth(200)
        self.btn_clear.setFixedWidth(200)
        
        lay3.addWidget(self.btn_add, alignment=Qt.AlignmentFlag.AlignCenter)
        lay3.addWidget(self.btn_clear, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(p3, stretch=1)

        return form_outer

    def _build_table_panel(self):
        table_outer = QFrame()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet("QFrame#table_outer { background-color: #2F2038; border: 1px solid #412B4E; border-radius: 6px; }")
        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)

        # Toolbar
        tools = QHBoxLayout()
        tools.addWidget(self._styled_label("Update Status:"))
        self.room_status_combo = QComboBox()
        self.room_status_combo.addItems(["AVAILABLE", "OCCUPIED", "MAINTENANCE"])
        self.room_status_combo.setFixedWidth(150)
        self.room_status_combo.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px;")
        tools.addWidget(self.room_status_combo)

        self.btn_set = self._action_button("Set Status", "#412B4E")
        self.btn_del = self._action_button("Delete Room", "#BE3455")
        self.btn_refresh = self._action_button("Refresh", "#412B4E")
        
        tools.addWidget(self.btn_set)
        tools.addWidget(self.btn_del)
        tools.addWidget(self.btn_refresh)
        tools.addStretch()
        layout.addLayout(tools)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Room No", "Type", "Price", "Cap", "Status", "Desc"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850; color: #F2F2F2;
                gridline-color: #412B4E; border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #412B4E; color: #FFE0E3;
                font-weight: bold; border: none; padding: 6px;
            }
            QTableWidget::item:selected { background-color: #BE3455; color: #FFE0E3; }
        """)
        
        layout.addWidget(self.table)
        return table_outer

    # --- UI Helpers ---
    def _create_sub_panel(self):
        p = QFrame()
        p.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        return p

    def _styled_label(self, t):
        l = QLabel(t)
        l.setStyleSheet("color: #FFE0E3; background: transparent; font-size: 11pt;")
        l.setFont(QFont("Segoe UI Semilight", 11))
        return l

    def _styled_input(self):
        e = QLineEdit()
        e.setFixedHeight(35)
        e.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px; padding-left: 8px;")
        return e

    def _action_button(self, t, bg_color):
        b = QPushButton(t)
        b.setFixedSize(110, 34)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        b.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: #FFE0E3;
                border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        return b

    # --- Data Methods ---
    def load_rooms(self, rooms):
        """Load rooms from database into table"""
        self.table.setRowCount(0)
        for r in rooms:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(r.get("room_number", "")))
            self.table.setItem(row, 2, QTableWidgetItem(r.get("room_type", "")))
            self.table.setItem(row, 3, QTableWidgetItem(str(r.get("price", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(str(r.get("capacity", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(r.get("status", "")))
            self.table.setItem(row, 6, QTableWidgetItem(r.get("description", "")))

    def get_selected_row(self):
        """Get the currently selected row"""
        selected = self.table.selectedItems()
        return selected[0].row() if selected else -1
    
    def get_table_value(self, row, col):
        """Get value from table cell"""
        item = self.table.item(row, col)
        return item.text() if item else ""
    
    def clearForm(self):
        """Clear all form fields"""
        self.room_number_field.clear()
        self.price_field.clear()
        self.capacity_field.clear()
        self.description_field.clear()
        self.room_type_combo.setCurrentIndex(0)
        self.table.clearSelection()
    
    def show_message(self, title, message, msg_type="info"):
        """Show message dialog"""
        if msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)
    
    def confirm_delete(self, room_number):
        """Confirm room deletion"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f'Delete room "{room_number}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoomPanel()
    window.resize(1100, 750)
    window.show()
    sys.exit(app.exec())