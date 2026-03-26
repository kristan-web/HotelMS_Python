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


class DeletedUserView(QWidget):
    """
    Deleted Users View.
    Displays deleted user accounts with option to restore.
    """
    
    # Signal to navigate back
    back_requested = pyqtSignal()
    restore_requested = pyqtSignal(dict)
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Deleted Users")
        self.setMinimumSize(900, 600)
        self.all_users = []  # Store all users for filtering
        self._build_ui()
        
    def _build_ui(self):
        self.setObjectName("del_user_root")
        self.setStyleSheet("""
            QWidget#del_user_root {
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
        
        title_lbl = QLabel("Deleted Users")
        title_lbl.setFont(QFont("Segoe UI Semilight", 24, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        
        sub_lbl = QLabel("Manage deleted accounts here")
        sub_lbl.setFont(QFont("Segoe UI Semilight", 14))
        sub_lbl.setStyleSheet("color: #A797A5; background: transparent;")
        
        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)
        
        title_row.addLayout(title_col)
        title_row.addStretch()
        
        self.restore_btn = QPushButton("Restore User")
        self.restore_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.restore_btn.setFixedHeight(42)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #A02848;
            }
        """)
        self.restore_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.restore_btn.clicked.connect(self.restore_user)
        title_row.addWidget(self.restore_btn)
        
        root.addLayout(title_row)
        
        # ── SEPARATOR ──────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #412B4E; border: none;")
        root.addWidget(sep)
        
        # ── TABLE PANEL ────────────────────────────────────────────────────
        table_panel = QWidget()
        table_panel.setObjectName("del_user_table_panel")
        table_panel.setStyleSheet("""
            QWidget#del_user_table_panel {
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
        self.search_input.setPlaceholderText("🔍  Search deleted users...")
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
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "User ID", "First Name", "Last Name", 
            "Contact No.", "Email", "Role"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setFont(QFont("Segoe UI Semilight", 11))
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
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
        
        btn_row.addWidget(self.back_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)
    
    def search_users(self):
        """Filter users based on search text"""
        search_text = self.get_search_text().lower()
        if not search_text:
            self._load_filtered_users()
        else:
            filtered = [u for u in self.all_users 
                       if search_text in u.get('first_name', '').lower() or 
                          search_text in u.get('last_name', '').lower() or
                          search_text in u.get('email', '').lower() or
                          search_text in u.get('phone', '').lower()]
            self._display_users(filtered)
    
    def _load_filtered_users(self):
        """Load filtered users"""
        self._display_users(self.all_users)
    
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
            
            # Color role based on type
            if role == "Admin":
                role_item.setForeground(QBrush(QColor(200, 40, 40)))  # Red
                role_item.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
            elif role == "Staff":
                role_item.setForeground(QBrush(QColor(30, 100, 200)))  # Blue
                role_item.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
            
            self.table.setItem(row, 5, role_item)
    
    def restore_user(self):
        """Restore selected user"""
        row = self.get_selected_row()
        if row >= 0:
            first_name = self.get_table_value(row, 1)
            last_name = self.get_table_value(row, 2)
            user_name = f"{first_name} {last_name}"
            
            if self.confirm_restore(user_name):
                user_data = {
                    'user_id': self.get_table_value(row, 0),
                    'first_name': first_name,
                    'last_name': last_name,
                    'phone': self.get_table_value(row, 3),
                    'email': self.get_table_value(row, 4),
                    'role': self.get_table_value(row, 5)
                }
                self.restore_requested.emit(user_data)
                self.show_message("Success", f"User '{user_name}' restored successfully!")
        else:
            self.show_message("No Selection", "Please select a user to restore.")
    
    def go_back(self):
        """Navigate back to user management view"""
        from views.AccountManagement.AccountAdministration.StaffAndAdminAccountView import StaffAndAdminAccountView
        self.account_view = StaffAndAdminAccountView(self.main_window)
        self.account_view.show()
        self.close()
    
    # ── PUBLIC METHODS ───────────────────────────────────────────────────────
    def load_users(self, users: list):
        """
        Load users into view
        users: list of dicts with keys: user_id, first_name, last_name, phone, email, role
        """
        self.all_users = users
        self._display_users(users)
    
    def get_selected_row(self) -> int:
        return self.table.currentRow()
    
    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""
    
    def get_search_text(self) -> str:
        return self.search_input.text().strip()
    
    def confirm_restore(self, name: str) -> bool:
        reply = QMessageBox.question(
            self, "Confirm Restore",
            f'Are you sure you want to restore user "{name}"?',
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
    w = DeletedUserView()
    
    # Sample data for testing
    sample_users = [
        {"user_id": 1, "first_name": "John", "last_name": "Doe", 
         "phone": "09123456789", "email": "john@example.com", "role": "Admin"},
        {"user_id": 2, "first_name": "Jane", "last_name": "Smith", 
         "phone": "09876543210", "email": "jane@example.com", "role": "Staff"},
        {"user_id": 3, "first_name": "Mike", "last_name": "Johnson", 
         "phone": "09111222333", "email": "mike@example.com", "role": "Staff"},
    ]
    
    w.load_users(sample_users)
    w.show()
    sys.exit(app.exec())