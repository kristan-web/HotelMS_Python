import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, 
    QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSizePolicy, QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from controllers.room_controller import get_room_controller


class RoomPanel(QWidget):
    def __init__(self): 
        super().__init__()
        self.controller = get_room_controller()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._build_ui()
        self._connect_signals()
        self.load_rooms()

    def _build_ui(self):
        self.setObjectName("room_root")
        self.setStyleSheet("QWidget#room_root { background-color: #2F2038; border: none; }")
        
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # ── TOP FORM PANEL (Like Reservation Panel) ──────────────────
        # ── TOP FORM PANEL (Like Reservation Panel) ──────────────────
        root_layout.addWidget(self._build_form_panel())
        
        # ── BOTTOM TABLE PANEL (Management Section) ──────────────────
        # ── BOTTOM TABLE PANEL (Management Section) ──────────────────
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
        self.btn_add.setFixedWidth(200) # Wider like Reservation Confirm
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

        # Table Setup (Synced style with Reservation Table)
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Room No", "Type", "Price", "Cap", "Status", "Desc"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850;
                color: #F2F2F2;
                gridline-color: #412B4E;
                border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #412B4E;
                color: #FFE0E3;
                font-weight: bold;
                border: none;
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #BE3455;
                color: #FFE0E3;
            }
        """)
        layout.addWidget(self.table)

        return table_outer

    def _connect_signals(self):
        """Connect button signals to controller methods."""
        self.btn_add.clicked.connect(self.add_room)
        self.btn_clear.clicked.connect(self.clear_form)
        self.btn_set.clicked.connect(self.update_status)
        self.btn_del.clicked.connect(self.delete_room)
        self.btn_refresh.clicked.connect(self.load_rooms)
        self.table.itemSelectionChanged.connect(self.fill_form_from_table)

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
                background-color: {bg_color};
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        return b

    # --- Validation ---
    def _validate_inputs(self) -> tuple:
        """Validate form inputs. Returns (is_valid, error_message)."""
        room_number = self.room_number_field.text().strip()
        if not room_number:
            return (False, "Room number is required.")
        
        try:
            price = float(self.price_field.text().strip())
            if price <= 0:
                return (False, "Price must be greater than 0.")
        except ValueError:
            return (False, "Invalid price format. Please enter a number.")
        
        try:
            capacity = int(self.capacity_field.text().strip())
            if capacity < 1:
                return (False, "Capacity must be at least 1.")
        except ValueError:
            return (False, "Invalid capacity format. Please enter a number.")
        
        return (True, "")

    # --- CRUD Operations ---
    def load_rooms(self):
        """Load all rooms from database."""
        rooms = self.controller.get_all()
        self._populate_table(rooms)

    def _populate_table(self, rooms):
        """Populate table with room data."""
        self.table.setRowCount(0)
        for r in rooms:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(r['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(r['room_number']))
            self.table.setItem(row, 2, QTableWidgetItem(r['room_type']))
            self.table.setItem(row, 3, QTableWidgetItem(f"{r['price']:.2f}"))
            self.table.setItem(row, 4, QTableWidgetItem(str(r['capacity'])))
            self.table.setItem(row, 5, QTableWidgetItem(r['status']))
            self.table.setItem(row, 6, QTableWidgetItem(r.get('description', '')))

    def fill_form_from_table(self):
        """Populate form fields with selected row data."""
        items = self.table.selectedItems()
        if not items:
            return
        row = items[0].row()
        self.room_number_field.setText(self.table.item(row, 1).text())
        self.room_type_combo.setCurrentText(self.table.item(row, 2).text())
        self.price_field.setText(self.table.item(row, 3).text())
        self.capacity_field.setText(self.table.item(row, 4).text())
        self.room_status_combo.setCurrentText(self.table.item(row, 5).text())
        self.description_field.setText(self.table.item(row, 6).text())

    def clear_form(self):
        """Clear all form fields."""
        self.room_number_field.clear()
        self.price_field.clear()
        self.capacity_field.clear()
        self.description_field.clear()
        self.room_type_combo.setCurrentIndex(0)
        self.room_status_combo.setCurrentIndex(0)
        self.table.clearSelection()

    def add_room(self):
        """Add a new room."""
        is_valid, error_msg = self._validate_inputs()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        room_number = self.room_number_field.text().strip()
        room_type = self.room_type_combo.currentText()
        price = float(self.price_field.text().strip())
        capacity = int(self.capacity_field.text().strip())
        description = self.description_field.text().strip()
        
        success, message = self.controller.create(
            room_number, room_type, price, capacity, description
        )
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_rooms()
            self.clear_form()
        else:
            QMessageBox.critical(self, "Error", message)

    def update_status(self):
        """Update status of selected room."""
        items = self.table.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "Please select a room to update.")
            return
        
        row = items[0].row()
        room_id = int(self.table.item(row, 0).text())
        new_status = self.room_status_combo.currentText()
        
        success, message = self.controller.update_status(room_id, new_status)
        
        if success:
            QMessageBox.information(self, "Success", message)
            self.load_rooms()
        else:
            QMessageBox.critical(self, "Error", message)

    def delete_room(self):
        """Delete selected room."""
        items = self.table.selectedItems()
        if not items:
            QMessageBox.warning(self, "No Selection", "Please select a room to delete.")
            return
        
        row = items[0].row()
        room_id = int(self.table.item(row, 0).text())
        room_number = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f'Delete room "{room_number}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.controller.delete(room_id)
            
            if success:
                QMessageBox.information(self, "Success", message)
                self.load_rooms()
                self.clear_form()
            else:
                QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoomPanel()
    window.resize(1100, 750)
    window.show()
    sys.exit(app.exec())