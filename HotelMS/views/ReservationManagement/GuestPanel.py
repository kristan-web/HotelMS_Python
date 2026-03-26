# GuestPanel.py - Simplified version that works
import sys
import os

# Add at the top of GuestPanel.py
from controllers.guest_controller import GuestController
from utils.db_connection import get_connection

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


class GuestPanelView(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = None
        self._build_ui()
        self.setup_controller()
    
    def setup_controller(self):
        """Setup database connection and controller"""
        try:
            db = get_connection()
            if db:
                self.controller = GuestController(db)
                self.controller.set_view(self)
                print("✓ Guest controller connected to database")
            else:
                print("✗ Could not connect to database")
                self.load_sample_data()
        except Exception as e:
            print(f"Error setting up controller: {e}")
            import traceback
            traceback.print_exc()
            self.load_sample_data()
        def load_sample_data(self):
            """Load sample data if database is not available"""
            sample_guests = [
                {"id": 1, "first_name": "Sample", "last_name": "Guest", 
                "email": "sample@email.com", "phone": "09123456789", "address": "Sample Address"},
            ]
            self.load_table(sample_guests)
            self.show_message("Info", "Using sample data. Database connection failed.", "warning")
    
    def _build_ui(self):
        self.setObjectName("guest_root")
        self.setStyleSheet("QWidget#guest_root { background-color: #2F2038; border: none; }")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # Add form panel
        root_layout.addWidget(self._build_form_panel())
        
        # Add table panel
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

        outer_layout = QHBoxLayout(form_outer)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        outer_layout.setSpacing(10)

        # Panel 1 — First Name / Last Name
        panel1 = QFrame()
        panel1.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        layout1 = QVBoxLayout(panel1)
        layout1.setContentsMargins(25, 14, 25, 14)
        
        lbl1 = QLabel("First name:")
        lbl1.setFont(QFont("Segoe UI Semilight", 11))
        lbl1.setStyleSheet("color: #FFE0E3;")
        layout1.addWidget(lbl1)
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setFixedHeight(32)
        self.first_name_input.setStyleSheet("background-color: #F9F5FF; border-radius: 4px; padding: 5px;")
        layout1.addWidget(self.first_name_input)
        
        lbl2 = QLabel("Last name:")
        lbl2.setFont(QFont("Segoe UI Semilight", 11))
        lbl2.setStyleSheet("color: #FFE0E3;")
        layout1.addWidget(lbl2)
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setFixedHeight(32)
        self.last_name_input.setStyleSheet("background-color: #F9F5FF; border-radius: 4px; padding: 5px;")
        layout1.addWidget(self.last_name_input)
        
        outer_layout.addWidget(panel1, stretch=1)

        # Panel 2 — Email / Address
        panel2 = QFrame()
        panel2.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        layout2 = QVBoxLayout(panel2)
        layout2.setContentsMargins(25, 14, 25, 14)
        
        lbl3 = QLabel("Email:")
        lbl3.setFont(QFont("Segoe UI Semilight", 11))
        lbl3.setStyleSheet("color: #FFE0E3;")
        layout2.addWidget(lbl3)
        
        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(32)
        self.email_input.setStyleSheet("background-color: #F9F5FF; border-radius: 4px; padding: 5px;")
        layout2.addWidget(self.email_input)
        
        lbl4 = QLabel("Address:")
        lbl4.setFont(QFont("Segoe UI Semilight", 11))
        lbl4.setStyleSheet("color: #FFE0E3;")
        layout2.addWidget(lbl4)
        
        self.address_input = QLineEdit()
        self.address_input.setFixedHeight(32)
        self.address_input.setStyleSheet("background-color: #F9F5FF; border-radius: 4px; padding: 5px;")
        layout2.addWidget(self.address_input)
        
        outer_layout.addWidget(panel2, stretch=1)

        # Panel 3 — Phone + buttons
        panel3 = QFrame()
        panel3.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        layout3 = QVBoxLayout(panel3)
        layout3.setContentsMargins(25, 14, 25, 14)
        
        lbl5 = QLabel("Phone:")
        lbl5.setFont(QFont("Segoe UI Semilight", 11))
        lbl5.setStyleSheet("color: #FFE0E3;")
        layout3.addWidget(lbl5)
        
        self.phone_input = QLineEdit()
        self.phone_input.setFixedHeight(32)
        self.phone_input.setStyleSheet("background-color: #F9F5FF; border-radius: 4px; padding: 5px;")
        layout3.addWidget(self.phone_input)
        layout3.addSpacing(12)
        
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Guest")
        self.add_btn.setFixedHeight(35)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE0E3;
                color: #2F2038;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #F0C8CC; }
        """)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(35)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        
        # Connect buttons to simple handlers
        self.add_btn.clicked.connect(self.show_add_message)
        self.clear_btn.clicked.connect(self.clear_form)
        
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.clear_btn)
        layout3.addLayout(btn_row)
        
        outer_layout.addWidget(panel3, stretch=1)

        return form_outer

    def _build_table_panel(self):
        table_outer = QFrame()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet("""
            QFrame#table_outer {
                background-color: #2F2038;
                border: 1px solid #412B4E;
                border-radius: 6px;
            }
        """)
        table_outer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Buttons row
        btn_row = QHBoxLayout()
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedSize(110, 34)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedSize(110, 34)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5A3D6B; }
        """)
        
        self.delete_btn.clicked.connect(self.show_delete_message)
        self.refresh_btn.clicked.connect(self.load_sample_data)
        
        btn_row.addWidget(self.delete_btn)
        btn_row.addWidget(self.refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Email", "Phone", "Address"])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setStretchLastSection(True)
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
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #BE3455;
                color: #FFE0E3;
            }
        """)
        
        layout.addWidget(self.table)
        return table_outer

    def load_sample_data(self):
        """Load sample data for testing"""
        sample_guests = [
            {"id": 1, "first_name": "John", "last_name": "Doe", "email": "john@email.com", "phone": "09123456789", "address": "Manila"},
            {"id": 2, "first_name": "Jane", "last_name": "Smith", "email": "jane@email.com", "phone": "09234567890", "address": "Makati"},
            {"id": 3, "first_name": "Maria", "last_name": "Santos", "email": "maria@email.com", "phone": "09345678901", "address": "Quezon City"},
        ]
        self.load_table(sample_guests)
    
    def load_table(self, guests):
        """Load guests into table"""
        self.table.setRowCount(0)
        for g in guests:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(g.get("id", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(g.get("first_name", "")))
            self.table.setItem(row, 2, QTableWidgetItem(g.get("last_name", "")))
            self.table.setItem(row, 3, QTableWidgetItem(g.get("email", "")))
            self.table.setItem(row, 4, QTableWidgetItem(g.get("phone", "")))
            self.table.setItem(row, 5, QTableWidgetItem(g.get("address", "")))
    
    def show_add_message(self):
        """Show message when add button is clicked"""
        QMessageBox.information(self, "Info", "Add Guest functionality coming soon!")
    
    def show_delete_message(self):
        """Show message when delete button is clicked"""
        selected = self.table.selectedItems()
        if selected:
            QMessageBox.information(self, "Info", "Delete Guest functionality coming soon!")
        else:
            QMessageBox.warning(self, "Warning", "Please select a guest to delete.")
    
    def clear_form(self):
        """Clear all form fields"""
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.table.clearSelection()
    
    def get_first_name(self): return self.first_name_input.text().strip()
    def get_last_name(self): return self.last_name_input.text().strip()
    def get_email(self): return self.email_input.text().strip()
    def get_address(self): return self.address_input.text().strip()
    def get_phone(self): return self.phone_input.text().strip()
    def get_selected_row(self): return self.table.currentRow()
    def get_table_value(self, row, col):
        item = self.table.item(row, col)
        return item.text() if item else ""
    def set_add_btn_text(self, text): self.add_btn.setText(text)
    def fill_form(self, first, last, email, address, phone):
        self.first_name_input.setText(first)
        self.last_name_input.setText(last)
        self.email_input.setText(email)
        self.address_input.setText(address)
        self.phone_input.setText(phone)
    def show_message(self, title, message, msg_type="info"):
        if msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)
    def confirm_delete(self, name):
        reply = QMessageBox.question(self, "Confirm Delete", f'Delete guest "{name}"?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = GuestPanelView()
    w.resize(1200, 700)
    w.show()
    sys.exit(app.exec())