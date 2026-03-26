import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QMessageBox, QAbstractItemView,
    QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor


class GuestPanelView(QWidget):
    
    # Signal definitions for controller communication
    add_guest_requested = pyqtSignal(dict)      # guest data dict
    edit_guest_requested = pyqtSignal(dict)     # guest data dict with id
    delete_guest_requested = pyqtSignal(str)    # guest_id
    refresh_requested = pyqtSignal()
    clear_form_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_guest_id = None
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        self.setObjectName("guest_root")
        self.setStyleSheet(
            "QWidget#guest_root { background-color: #2F2038; border: none; }")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # ── TOP FORM PANEL ─────────────────────────────────────────────────
        root_layout.addWidget(self._build_form_panel())

        # ── BOTTOM TABLE PANEL ─────────────────────────────────────────────
        root_layout.addWidget(self._build_table_panel(), stretch=1)

    def _connect_signals(self):
        """Connect internal signals"""
        self.add_btn.clicked.connect(self.handle_add_guest)
        self.delete_btn.clicked.connect(self.handle_delete_guest)
        self.refresh_btn.clicked.connect(self.handle_refresh)
        self.clear_btn.clicked.connect(self.handle_clear_form)
        self.table.itemSelectionChanged.connect(self.fill_form_from_selection)

    # ── FORM PANEL (3 dark-purple sub-panels side by side) ──────────────────
    def _build_form_panel(self):
        form_outer = QWidget()
        form_outer.setObjectName("form_outer")
        form_outer.setStyleSheet("""
            QWidget#form_outer {
                background-color: #2F2038;
                border: 1px solid #412B4E;
                border-radius: 6px;
            }
        """)

        outer_layout = QHBoxLayout(form_outer)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(10)

        # Panel 1 — First Name / Last Name
        outer_layout.addWidget(
            self._build_input_sub_panel([
                ("First name:*", "first_name"),
                ("Last name:*",  "last_name"),
            ]),
            stretch=1
        )

        # Panel 2 — Email / Address
        outer_layout.addWidget(
            self._build_input_sub_panel([
                ("Email:*",   "email"),
                ("Address:*", "address"),
            ]),
            stretch=1
        )

        # Panel 3 — Phone + buttons
        outer_layout.addWidget(self._build_action_sub_panel(), stretch=1)

        return form_outer

    def _build_input_sub_panel(self, fields: list) -> QWidget:
        """Build a sub-panel with label+input pairs."""
        panel = QWidget()
        panel.setObjectName("sub_panel")
        panel.setStyleSheet("""
            QWidget#sub_panel {
                background-color: #3D2850;
                border-radius: 6px;
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 14, 25, 14)
        layout.setSpacing(4)
        layout.addStretch()

        for label_text, attr_name in fields:
            lbl = QLabel(label_text)
            lbl.setFont(QFont("Segoe UI Semilight", 11))
            lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
            layout.addWidget(lbl)

            field = QLineEdit()
            field.setFont(QFont("Segoe UI Semilight", 11))
            field.setFixedHeight(32)
            field.setStyleSheet("""
                QLineEdit {
                    background-color: #F9F5FF;
                    color: #2F2038;
                    border: 1px solid #A797A5;
                    border-radius: 4px;
                    padding: 2px 8px;
                }
                QLineEdit:focus {
                    border: 1px solid #BE3455;
                }
            """)
            setattr(self, f"{attr_name}_input", field)
            layout.addWidget(field)
            layout.addSpacing(4)

        layout.addStretch()
        return panel

    def _build_action_sub_panel(self) -> QWidget:
        """Build the Phone + Add/Clear buttons sub-panel."""
        panel = QWidget()
        panel.setObjectName("action_panel")
        panel.setStyleSheet("""
            QWidget#action_panel {
                background-color: #3D2850;
                border-radius: 6px;
                border: none;
            }
        """)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 14, 25, 14)
        layout.setSpacing(4)
        layout.addStretch()

        # Phone field
        phone_lbl = QLabel("Phone:*")
        phone_lbl.setFont(QFont("Segoe UI Semilight", 11))
        phone_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        layout.addWidget(phone_lbl)

        self.phone_input = QLineEdit()
        self.phone_input.setFont(QFont("Segoe UI Semilight", 11))
        self.phone_input.setFixedHeight(32)
        self.phone_input.setStyleSheet("""
            QLineEdit {
                background-color: #F9F5FF;
                color: #2F2038;
                border: 1px solid #A797A5;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QLineEdit:focus { border: 1px solid #BE3455; }
        """)
        layout.addWidget(self.phone_input)
        layout.addSpacing(12)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.add_btn = QPushButton("Add Guest")
        self.add_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(35)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE0E3;
                color: #2F2038;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #F0C8CC; }
        """)
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.clear_btn.setFixedHeight(35)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.clear_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.clear_btn)
        layout.addLayout(btn_row)
        layout.addStretch()

        return panel

    # ── TABLE PANEL ──────────────────────────────────────────────────────────
    def _build_table_panel(self):
        table_outer = QWidget()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet("""
            QWidget#table_outer {
                background-color: #2F2038;
                border: 1px solid #412B4E;
                border-radius: 6px;
            }
        """)
        table_outer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # ── Action buttons row ──────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.delete_btn.setFixedSize(110, 34)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.delete_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.refresh_btn.setFixedSize(110, 34)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #5A3D6B; }
        """)
        self.refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # ── Table ───────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "First Name", "Last Name", "Email", "Phone", "Address"])
        self.table.setColumnHidden(0, True)  # Hide ID column
        self.table.setFont(QFont("Segoe UI Semilight", 11))
        self.table.setRowHeight(0, 40)
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850;
                color: #F2F2F2;
                border: none;
                border-radius: 4px;
                gridline-color: #412B4E;
                font-size: 12px;
            }
            QTableWidget::item:selected {
                background-color: #BE3455;
                color: #FFE0E3;
            }
            QTableWidget::item:hover {
                background-color: #5A3D6B;
            }
            QHeaderView::section {
                background-color: #412B4E;
                color: #FFE0E3;
                font-weight: bold;
                font-size: 12px;
                padding: 6px;
                border: none;
                border-bottom: 1px solid #2F2038;
            }
            QScrollBar:vertical {
                background: #2F2038;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #412B4E;
                border-radius: 4px;
            }
        """)

        layout.addWidget(self.table)
        return table_outer

    # ── EVENT HANDLERS (Emit Signals) ───────────────────────────────────────
    def handle_add_guest(self):
        """Emit add_guest signal with form data"""
        guest_data = {
            'first_name': self.get_first_name(),
            'last_name': self.get_last_name(),
            'email': self.get_email(),
            'address': self.get_address(),
            'phone': self.get_phone()
        }
        
        # Check if editing existing guest
        if self.current_guest_id:
            guest_data['id'] = self.current_guest_id
            self.edit_guest_requested.emit(guest_data)
        else:
            self.add_guest_requested.emit(guest_data)

    def handle_delete_guest(self):
        """Emit delete_guest signal for selected row"""
        row = self.get_selected_row()
        if row >= 0:
            guest_id = self.get_table_value(row, 0)
            guest_name = f"{self.get_table_value(row, 1)} {self.get_table_value(row, 2)}"
            if self.confirm_delete(guest_name):
                self.delete_guest_requested.emit(guest_id)
        else:
            self.show_message("No Selection", "Please select a guest to delete.", "warning")

    def handle_refresh(self):
        """Emit refresh signal"""
        self.refresh_requested.emit()

    def handle_clear_form(self):
        """Emit clear form signal"""
        self.current_guest_id = None
        self.add_btn.setText("Add Guest")
        self.clear_form_requested.emit()
        self._clear_form_fields()

    def fill_form_from_selection(self):
        """Populate form fields with selected guest data for editing"""
        row = self.get_selected_row()
        if row >= 0:
            self.current_guest_id = self.get_table_value(row, 0)
            self.first_name_input.setText(self.get_table_value(row, 1))
            self.last_name_input.setText(self.get_table_value(row, 2))
            self.email_input.setText(self.get_table_value(row, 3))
            self.phone_input.setText(self.get_table_value(row, 4))
            self.address_input.setText(self.get_table_value(row, 5))
            self.add_btn.setText("Update Guest")

    def _clear_form_fields(self):
        """Clear all form input fields"""
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.phone_input.clear()
        self.address_input.clear()
        self.current_guest_id = None
        self.add_btn.setText("Add Guest")

    # ── PUBLIC GETTERS ─────────────────────────────────────────────────────
    def get_first_name(self) -> str:
        return self.first_name_input.text().strip()

    def get_last_name(self) -> str:
        return self.last_name_input.text().strip()

    def get_email(self) -> str:
        return self.email_input.text().strip()

    def get_address(self) -> str:
        return self.address_input.text().strip()

    def get_phone(self) -> str:
        return self.phone_input.text().strip()

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""

    # ── PUBLIC SETTERS (called by controller) ───────────────────────────────
    def set_add_btn_text(self, text: str):
        self.add_btn.setText(text)

    def fill_form(self, first: str, last: str, email: str,
                  address: str, phone: str, guest_id: str = None):
        self.first_name_input.setText(first)
        self.last_name_input.setText(last)
        self.email_input.setText(email)
        self.address_input.setText(address)
        self.phone_input.setText(phone)
        if guest_id:
            self.current_guest_id = guest_id
            self.add_btn.setText("Update Guest")
        else:
            self.current_guest_id = None
            self.add_btn.setText("Add Guest")

    def clear_form(self):
        """Clear form and reset to add mode"""
        self._clear_form_fields()
        self.table.clearSelection()

    def load_table(self, guests: list):
        """
        guests: list of dicts with keys:
        id, first_name, last_name, email, phone, address
        """
        self.table.setRowCount(0)
        for g in guests:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)
            for col, key in enumerate(
                    ["id", "first_name", "last_name", "email", "phone", "address"]):
                item = QTableWidgetItem(str(g.get(key, "")))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter |
                                      Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, col, item)

    def show_message(self, title: str, message: str,
                     msg_type: str = "info"):
        if msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)

    def confirm_delete(self, name: str) -> bool:
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f'Delete guest "{name}"?\nThis will also remove all their reservations.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)

    w = GuestPanelView()
    w.setWindowTitle("Guest Panel — Preview")
    w.resize(1200, 700)

    # Load some dummy data for preview
    w.load_table([
        {"id": 1, "first_name": "Juan",  "last_name": "Dela Cruz",
         "email": "juan@email.com", "phone": "09171234567",
         "address": "Manila"},
        {"id": 2, "first_name": "Maria", "last_name": "Santos",
         "email": "maria@email.com", "phone": "09281234567",
         "address": "Quezon City"},
    ])

    w.show()
    sys.exit(app.exec())