import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QSizePolicy, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor, QBrush


class StaffAndAdminAccountView(QWidget):
    """
    Staff and Admin Account Management View.
    Displays all user accounts with options to edit, delete, and create new accounts.
    """
    
    # Signal definitions for controller communication
    back_requested = pyqtSignal()
    edit_requested = pyqtSignal(dict)      # user data dict
    delete_requested = pyqtSignal(str)     # user_id
    create_admin_requested = pyqtSignal()
    create_staff_requested = pyqtSignal()
    view_deleted_requested = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Account Management")
        self.setMinimumSize(900, 650)
        self.all_users = []
        self._build_ui()
        
    def _build_ui(self):
        self.setObjectName("user_root")
        self.setStyleSheet("""
            QWidget#user_root {
                background-color: #2F2038;
                border: none;
            }
        """)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)
        
        # ── TITLE ROW ──────────────────────────────────────────────────────
        title_row = QHBoxLayout()
        
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        
        title_lbl = QLabel("Account Management")
        title_lbl.setFont(QFont("Segoe UI Semilight", 24, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        
        sub_lbl = QLabel("Manage staff and admin accounts here")
        sub_lbl.setFont(QFont("Segoe UI Semilight", 14))
        sub_lbl.setStyleSheet("color: #A797A5; background: transparent;")
        
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        
        title_row.addLayout(title_col)
        title_row.addStretch()
        
        self.deleted_btn = QPushButton("View Deleted Accounts")
        self.deleted_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.deleted_btn.setFixedHeight(42)
        self.deleted_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover {
                background-color: #5A3D6B;
            }
        """)
        self.deleted_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.deleted_btn.clicked.connect(self.view_deleted)
        title_row.addWidget(self.deleted_btn)
        
        root.addLayout(title_row)
        
        # ── SEPARATOR ──────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #412B4E; border: none;")
        root.addWidget(sep)
        
        # ── TABLE PANEL ────────────────────────────────────────────────────
        table_panel = QWidget()
        table_panel.setObjectName("user_table_panel")
        table_panel.setStyleSheet("""
            QWidget#user_table_panel {
                background-color: #3D2850;
                border: 2px solid #412B4E;
                border-radius: 6px;
            }
        """)
        table_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        panel_layout = QVBoxLayout(table_panel)
        panel_layout.setContentsMargins(8, 8, 8, 8)
        panel_layout.setSpacing(6)
        
        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search users...")
        self.search_input.setFont(QFont("Segoe UI Semilight", 11))
        self.search_input.setFixedHeight(32)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #F9F5FF;
                color: #2F2038;
                border: 1px solid #A797A5;
                border-radius: 4px;
                padding: 2px 10px;
            }
            QLineEdit:focus {
                border: 1px solid #BE3455;
            }
        """)
        self.search_input.textChanged.connect(self.search_users)
        panel_layout.addWidget(self.search_input)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "User ID", "First Name", "Last Name", 
            "Contact No.", "Email", "Role", "Actions"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setFont(QFont("Segoe UI Semilight", 11))
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 160)
        self.table.setShowGrid(True)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850;
                color: #F2F2F2;
                border: none;
                gridline-color: #412B4E;
            }
            QTableWidget::item:selected {
                background-color: #BE3455;
                color: #FFE0E3;
            }
            QTableWidget::item:hover {
                background-color: #BE3455;
                color: #FFE0E3;
            }
            QHeaderView::section {
                background-color: #412B4E;
                color: #FFE0E3;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #2F2038;
                border-bottom: 1px solid #2F2038;
            }
            QTableCornerButton::section {
                background-color: #412B4E;
                border: none;
                border-right: 1px solid #2F2038;
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
            QScrollBar::handle:vertical:hover {
                background: #BE3455;
            }
        """)
        
        # Fix vertical header background
        self.table.verticalHeader().setStyleSheet("background-color: #412B4E;")
        
        panel_layout.addWidget(self.table, stretch=1)
        
        root.addWidget(table_panel, stretch=1)
        
        # ── BOTTOM BUTTONS ─────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.back_btn = QPushButton("← Go Back")
        self.back_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.back_btn.setFixedHeight(42)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover {
                background-color: #5A3D6B;
            }
        """)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.clicked.connect(self.go_back)
        
        self.create_admin_btn = QPushButton("Create New Admin Account")
        self.create_admin_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.create_admin_btn.setFixedHeight(42)
        self.create_admin_btn.setStyleSheet("""
            QPushButton {
                background-color: #8C263E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover {
                background-color: #6B1E30;
            }
        """)
        self.create_admin_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.create_admin_btn.clicked.connect(self.create_admin)
        
        self.create_staff_btn = QPushButton("Create New Staff Account")
        self.create_staff_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.create_staff_btn.setFixedHeight(42)
        self.create_staff_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover {
                background-color: #A02848;
            }
        """)
        self.create_staff_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.create_staff_btn.clicked.connect(self.create_staff)
        
        btn_row.addWidget(self.back_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.create_admin_btn)
        btn_row.addWidget(self.create_staff_btn)
        root.addLayout(btn_row)
    
    def _make_row_buttons(self, row: int):
        """Creates Edit + Delete buttons for each table row."""
        cell_widget = QWidget()
        cell_widget.setObjectName("row_btn_widget")
        cell_widget.setStyleSheet(
            "QWidget#row_btn_widget { background-color: transparent; border: none; }")
        
        layout = QHBoxLayout(cell_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        edit_btn = QPushButton("✏ Edit")
        edit_btn.setFixedHeight(30)
        edit_btn.setFont(QFont("Segoe UI Semilight", 9, QFont.Weight.Bold))
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 4px;
                padding: 0 8px;
            }
            QPushButton:hover {
                background-color: #5A3D6B;
            }
        """)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(lambda _, r=row: self.edit_user(r))
        
        del_btn = QPushButton("🗑 Delete")
        del_btn.setFixedHeight(30)
        del_btn.setFont(QFont("Segoe UI Semilight", 9, QFont.Weight.Bold))
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 4px;
                padding: 0 8px;
            }
            QPushButton:hover {
                background-color: #A02848;
            }
        """)
        del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        del_btn.clicked.connect(lambda _, r=row: self.confirm_and_delete(r))
        
        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
        
        return cell_widget, edit_btn, del_btn
    
    def confirm_and_delete(self, row):
        """Confirm and emit delete signal"""
        user_name = f"{self.get_table_value(row, 1)} {self.get_table_value(row, 2)}"
        if self.confirm_delete(user_name):
            user_id = self.get_table_value(row, 0)
            self.delete_requested.emit(user_id)
    
    def search_users(self):
        """Filter users based on search text"""
        search_text = self.get_search_text().lower()
        if not search_text:
            self._display_users(self.all_users)
        else:
            filtered = [u for u in self.all_users 
                       if search_text in u.get('first_name', '').lower() or 
                          search_text in u.get('last_name', '').lower() or
                          search_text in u.get('email', '').lower() or
                          search_text in u.get('phone', '').lower()]
            self._display_users(filtered)
    
    def _display_users(self, users):
        """Display users in table"""
        self.table.setRowCount(0)
        
        for u in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)
            
            self.table.setItem(row, 0, QTableWidgetItem(str(u.get('user_id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(u.get('first_name', ''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(u.get('last_name', ''))))
            self.table.setItem(row, 3, QTableWidgetItem(str(u.get('phone', ''))))
            self.table.setItem(row, 4, QTableWidgetItem(str(u.get('email', ''))))
            
            # Role item with color
            role = str(u.get('role', ''))
            role_item = QTableWidgetItem(role)
            if role == "Admin":
                role_item.setForeground(QBrush(QColor(200, 40, 40)))
                role_item.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
            elif role == "Staff":
                role_item.setForeground(QBrush(QColor(30, 100, 200)))
                role_item.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
            self.table.setItem(row, 5, role_item)
            
            # Actions column
            cell, edit_btn, del_btn = self._make_row_buttons(row)
            self.table.setCellWidget(row, 6, cell)
    
    def edit_user(self, row):
        """Open edit user dialog - emit signal with user data"""
        user_data = {
            'user_id': self.get_table_value(row, 0),
            'first_name': self.get_table_value(row, 1),
            'last_name': self.get_table_value(row, 2),
            'phone': self.get_table_value(row, 3),
            'email': self.get_table_value(row, 4),
            'role': self.get_table_value(row, 5)
        }
        self.edit_requested.emit(user_data)
    
    def view_deleted(self):
        """Emit signal to open deleted users view"""
        self.view_deleted_requested.emit()
    
    def create_admin(self):
        """Emit signal to open admin registration view"""
        self.create_admin_requested.emit()
    
    def create_staff(self):
        """Emit signal to open staff registration view"""
        self.create_staff_requested.emit()
    
    def go_back(self):
        """Navigate back to dashboard"""
        self.back_requested.emit()
        self.close()
    
    # ── PUBLIC METHODS ───────────────────────────────────────────────────────
    def load_users(self, users: list):
        """Load users into view"""
        self.all_users = users
        self._display_users(users)
    
    def get_selected_row(self) -> int:
        return self.table.currentRow()
    
    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""
    
    def get_search_text(self) -> str:
        return self.search_input.text().strip()
    
    def confirm_delete(self, name: str) -> bool:
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f'Delete user "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)
    
    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    w = StaffAndAdminAccountView()
    
    sample_users = [
        {"user_id": 1, "first_name": "John", "last_name": "Doe", 
         "phone": "09123456789", "email": "john@example.com", "role": "Admin"},
        {"user_id": 2, "first_name": "Jane", "last_name": "Smith", 
         "phone": "09876543210", "email": "jane@example.com", "role": "Staff"},
    ]
    
    w.load_users(sample_users)
    w.show()
    sys.exit(app.exec())