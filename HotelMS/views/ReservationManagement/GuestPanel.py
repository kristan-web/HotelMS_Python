# views/ReservationManagement/GuestPanel.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QVBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QSizePolicy, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QCursor

# Import from controllers
from controllers.guest_controller import GuestController
from utils.db_connection import get_connection


class GuestPanelView(QWidget):
    def __init__(self):
        super().__init__()
        print("GuestPanelView initialized")
        self.controller = None
        self._build_ui()
        self._setup_controller()
    
    def _setup_controller(self):
        """Setup the controller with database connection"""
        try:
            db_connection = get_connection()
            if db_connection:
                self.controller = GuestController(db_connection)
                self.controller.set_view(self)
                print("✓ Guest controller initialized")
            else:
                print("✗ Could not get database connection for guest panel")
        except Exception as e:
            print(f"Error setting up guest controller: {e}")

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
        panel1 = QWidget()
        panel1.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        layout1 = QVBoxLayout(panel1)
        layout1.setContentsMargins(25, 14, 25, 14)
        
        lbl1 = QLabel("First name:")
        lbl1.setFont(QFont("Segoe UI Semilight", 11))
        lbl1.setStyleSheet("color: #FFE0E3;")
        layout1.addWidget(lbl1)
        
        self.first_name_input = QLineEdit()
        self.first_name_input.setFixedHeight(32)
        layout1.addWidget(self.first_name_input)
        
        lbl2 = QLabel("Last name:")
        lbl2.setFont(QFont("Segoe UI Semilight", 11))
        lbl2.setStyleSheet("color: #FFE0E3;")
        layout1.addWidget(lbl2)
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setFixedHeight(32)
        layout1.addWidget(self.last_name_input)
        
        outer_layout.addWidget(panel1, stretch=1)

        # Panel 2 — Email / Address
        panel2 = QWidget()
        panel2.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        layout2 = QVBoxLayout(panel2)
        layout2.setContentsMargins(25, 14, 25, 14)
        
        lbl3 = QLabel("Email:")
        lbl3.setFont(QFont("Segoe UI Semilight", 11))
        lbl3.setStyleSheet("color: #FFE0E3;")
        layout2.addWidget(lbl3)
        
        self.email_input = QLineEdit()
        self.email_input.setFixedHeight(32)
        layout2.addWidget(self.email_input)
        
        lbl4 = QLabel("Address:")
        lbl4.setFont(QFont("Segoe UI Semilight", 11))
        lbl4.setStyleSheet("color: #FFE0E3;")
        layout2.addWidget(lbl4)
        
        self.address_input = QLineEdit()
        self.address_input.setFixedHeight(32)
        layout2.addWidget(self.address_input)
        
        outer_layout.addWidget(panel2, stretch=1)

        # Panel 3 — Phone + buttons
        panel3 = QWidget()
        panel3.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        layout3 = QVBoxLayout(panel3)
        layout3.setContentsMargins(25, 14, 25, 14)
        
        lbl5 = QLabel("Phone:")
        lbl5.setFont(QFont("Segoe UI Semilight", 11))
        lbl5.setStyleSheet("color: #FFE0E3;")
        layout3.addWidget(lbl5)
        
        self.phone_input = QLineEdit()
        self.phone_input.setFixedHeight(32)
        layout3.addWidget(self.phone_input)
        layout3.addSpacing(12)
        
        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Guest")
        self.add_btn.setFixedHeight(35)
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setFixedHeight(35)
        
        btn_row.addWidget(self.add_btn)
        btn_row.addWidget(self.clear_btn)
        layout3.addLayout(btn_row)
        
        outer_layout.addWidget(panel3, stretch=1)

        return form_outer

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
        table_outer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Search bar and buttons row
        top_bar = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setFont(QFont("Segoe UI Semilight", 11))
        search_label.setStyleSheet("color: #FFE0E3;")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, email, or phone...")
        self.search_input.setFixedHeight(34)
        
        top_bar.addWidget(search_label)
        top_bar.addWidget(self.search_input, stretch=1)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setFixedSize(110, 34)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setFixedSize(110, 34)
        
        top_bar.addWidget(self.delete_btn)
        top_bar.addWidget(self.refresh_btn)
        layout.addLayout(top_bar)

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

    # Public methods
    def get_first_name(self): 
        return self.first_name_input.text().strip()
    
    def get_last_name(self): 
        return self.last_name_input.text().strip()
    
    def get_email(self): 
        return self.email_input.text().strip()
    
    def get_address(self): 
        return self.address_input.text().strip()
    
    def get_phone(self): 
        return self.phone_input.text().strip()
    
    def get_selected_row(self): 
        return self.table.currentRow()
    
    def get_table_value(self, row, col):
        item = self.table.item(row, col)
        return item.text() if item else ""
    
    def set_add_btn_text(self, text): 
        self.add_btn.setText(text)
    
    def fill_form(self, first, last, email, address, phone):
        self.first_name_input.setText(first)
        self.last_name_input.setText(last)
        self.email_input.setText(email)
        self.address_input.setText(address)
        self.phone_input.setText(phone)
    
    def clear_form(self):
        self.first_name_input.clear()
        self.last_name_input.clear()
        self.email_input.clear()
        self.address_input.clear()
        self.phone_input.clear()
        self.table.clearSelection()
        self.add_btn.setText("Add Guest")
    
    def load_table(self, guests):
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
    
    def show_message(self, title, message, msg_type="info"):
        if msg_type == "warning":
            QMessageBox.warning(self, title, message)
        elif msg_type == "error":
            QMessageBox.critical(self, title, message)
        else:
            QMessageBox.information(self, title, message)
    
    def confirm_delete(self, name):
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f'Delete guest "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = GuestPanelView()
    w.resize(1200, 700)
    w.show()
    sys.exit(app.exec())