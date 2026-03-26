import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


class EditUserView(QDialog):
    """
    Edit User Dialog.
    Allows editing of user details including role.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit User Details")
        self.setModal(True)
        self.setFixedSize(520, 500)
        self._user_id = None
        self._build_ui()
    
    def _build_ui(self):
        self.setStyleSheet("background-color: #2F2038;")
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        # Header
        header = QWidget()
        header.setStyleSheet("background-color: #FFE0E3;")
        header.setFixedHeight(48)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        title = QLabel("Edit User Details")
        title.setFont(QFont("Segoe UI Semilight", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038;")
        header_layout.addWidget(title)
        root.addWidget(header)
        
        # Form Body
        body = QWidget()
        body.setStyleSheet("background-color: #2F2038;")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)
        
        # Row 1: First Name | Last Name
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        first_name_col = QVBoxLayout()
        first_name_lbl = QLabel("First Name: *")
        first_name_lbl.setFont(QFont("Segoe UI Semilight", 11))
        first_name_lbl.setStyleSheet("color: #FFE0E3;")
        self.first_name_input = self._make_input()
        first_name_col.addWidget(first_name_lbl)
        first_name_col.addWidget(self.first_name_input)
        
        last_name_col = QVBoxLayout()
        last_name_lbl = QLabel("Last Name: *")
        last_name_lbl.setFont(QFont("Segoe UI Semilight", 11))
        last_name_lbl.setStyleSheet("color: #FFE0E3;")
        self.last_name_input = self._make_input()
        last_name_col.addWidget(last_name_lbl)
        last_name_col.addWidget(self.last_name_input)
        
        row1.addLayout(first_name_col)
        row1.addLayout(last_name_col)
        body_layout.addLayout(row1)
        
        # Email
        email_lbl = QLabel("Email Address: *")
        email_lbl.setFont(QFont("Segoe UI Semilight", 11))
        email_lbl.setStyleSheet("color: #FFE0E3;")
        self.email_input = self._make_input()
        body_layout.addWidget(email_lbl)
        body_layout.addWidget(self.email_input)
        
        # Phone
        phone_lbl = QLabel("Contact Number: *")
        phone_lbl.setFont(QFont("Segoe UI Semilight", 11))
        phone_lbl.setStyleSheet("color: #FFE0E3;")
        self.phone_input = self._make_input()
        body_layout.addWidget(phone_lbl)
        body_layout.addWidget(self.phone_input)
        
        # Role
        role_lbl = QLabel("Role: *")
        role_lbl.setFont(QFont("Segoe UI Semilight", 11))
        role_lbl.setStyleSheet("color: #FFE0E3;")
        self.role_input = QComboBox()
        self.role_input.addItems(["Admin", "Staff"])
        self.role_input.setFont(QFont("Segoe UI Semilight", 11))
        self.role_input.setFixedHeight(34)
        self.role_input.setStyleSheet("""
            QComboBox {
                background-color: #F9F5FF;
                color: #2F2038;
                border: 1px solid #A797A5;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QComboBox:focus { border: 1px solid #BE3455; }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #3D2850;
                color: #FFE0E3;
                selection-background-color: #BE3455;
            }
        """)
        body_layout.addWidget(role_lbl)
        body_layout.addWidget(self.role_input)
        
        body_layout.addStretch()
        
        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        
        self.update_btn = self._make_button("Update", "#BE3455", "#FFE0E3")
        self.cancel_btn = self._make_button("Cancel", "#412B4E", "#FFE0E3")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_row.addWidget(self.update_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        body_layout.addLayout(btn_row)
        
        root.addWidget(body)
        
        # Hidden user ID field
        self.user_id_input = QLineEdit()
        self.user_id_input.hide()
    
    def _make_input(self) -> QLineEdit:
        field = QLineEdit()
        field.setFont(QFont("Segoe UI Semilight", 11))
        field.setFixedHeight(34)
        field.setStyleSheet("""
            QLineEdit {
                background-color: #F9F5FF;
                color: #2F2038;
                border: 1px solid #A797A5;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QLineEdit:focus { border: 1px solid #BE3455; }
        """)
        return field
    
    def _make_button(self, text: str, bg: str, fg: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        btn.setFixedSize(90, 40)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: none;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {"#A02848" if bg == "#BE3455" else "#5A3D6B"};
            }}
        """)
        return btn
    
    # ── PUBLIC METHODS ───────────────────────────────────────────────────────
    def load_user_data(self, user_id: str, first_name: str, last_name: str,
                       email: str, phone: str, role: str):
        """Load user data into the form"""
        self._user_id = user_id
        self.user_id_input.setText(user_id)
        self.first_name_input.setText(first_name)
        self.last_name_input.setText(last_name)
        self.email_input.setText(email)
        self.phone_input.setText(phone)
        self.role_input.setCurrentText(role)
    
    def get_user_id(self) -> str:
        return self.user_id_input.text().strip()
    
    def get_first_name(self) -> str:
        return self.first_name_input.text().strip()
    
    def get_last_name(self) -> str:
        return self.last_name_input.text().strip()
    
    def get_email(self) -> str:
        return self.email_input.text().strip()
    
    def get_phone(self) -> str:
        return self.phone_input.text().strip()
    
    def get_role(self) -> str:
        return self.role_input.currentText()
    
    def get_user_data(self) -> dict:
        return {
            'user_id': self.get_user_id(),
            'first_name': self.get_first_name(),
            'last_name': self.get_last_name(),
            'email': self.get_email(),
            'phone': self.get_phone(),
            'role': self.get_role()
        }
    
    def validate_inputs(self) -> bool:
        if not self.get_first_name():
            QMessageBox.warning(self, "Error", "Please enter first name.")
            return False
        if not self.get_last_name():
            QMessageBox.warning(self, "Error", "Please enter last name.")
            return False
        if not self.get_email():
            QMessageBox.warning(self, "Error", "Please enter email address.")
            return False
        if not self.get_phone():
            QMessageBox.warning(self, "Error", "Please enter contact number.")
            return False
        return True
    
    def accept(self):
        if self.validate_inputs():
            super().accept()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = EditUserView()
    dlg.load_user_data("1", "John", "Doe", "john@example.com", "09123456789", "Admin")
    dlg.show()
    sys.exit(app.exec())