import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


class EditGuestView(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Guest Details")
        self.setModal(True)
        self.setFixedSize(520, 480)
        self._guest_id = None
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
        
        title = QLabel("Edit Guest Details")
        title.setFont(QFont("Segoe UI Semilight", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038;")
        header_layout.addWidget(title)
        root.addWidget(header)

        # Form Body
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)

        # First Name & Last Name row
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        # First Name
        first_name_col = QVBoxLayout()
        first_name_lbl = QLabel("First Name: *")
        first_name_lbl.setStyleSheet("color: #FFE0E3;")
        self.first_name_input = self._make_input()
        first_name_col.addWidget(first_name_lbl)
        first_name_col.addWidget(self.first_name_input)
        
        # Last Name
        last_name_col = QVBoxLayout()
        last_name_lbl = QLabel("Last Name: *")
        last_name_lbl.setStyleSheet("color: #FFE0E3;")
        self.last_name_input = self._make_input()
        last_name_col.addWidget(last_name_lbl)
        last_name_col.addWidget(self.last_name_input)
        
        row1.addLayout(first_name_col)
        row1.addLayout(last_name_col)
        body_layout.addLayout(row1)

        # Email
        email_lbl = QLabel("Email Address: *")
        email_lbl.setStyleSheet("color: #FFE0E3;")
        self.email_input = self._make_input()
        body_layout.addWidget(email_lbl)
        body_layout.addWidget(self.email_input)

        # Phone
        phone_lbl = QLabel("Contact Number: *")
        phone_lbl.setStyleSheet("color: #FFE0E3;")
        self.phone_input = self._make_input()
        body_layout.addWidget(phone_lbl)
        body_layout.addWidget(self.phone_input)

        # Address
        address_lbl = QLabel("Address: *")
        address_lbl.setStyleSheet("color: #FFE0E3;")
        self.address_input = self._make_input()
        body_layout.addWidget(address_lbl)
        body_layout.addWidget(self.address_input)

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

        # Hidden guest ID field
        self.guest_id_input = QLineEdit()
        self.guest_id_input.hide()

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
            QPushButton:hover {{ background-color: {"#A02848" if bg == "#BE3455" else "#5A3D6B"}; }}
        """)
        return btn

    def load_guest_data(self, guest_id, first_name, last_name, email, phone, address):
        self._guest_id = guest_id
        self.guest_id_input.setText(guest_id)
        self.first_name_input.setText(first_name)
        self.last_name_input.setText(last_name)
        self.email_input.setText(email)
        self.phone_input.setText(phone)
        self.address_input.setText(address)

    def get_guest_id(self):
        return self.guest_id_input.text().strip()

    def get_first_name(self):
        return self.first_name_input.text().strip()

    def get_last_name(self):
        return self.last_name_input.text().strip()

    def get_email(self):
        return self.email_input.text().strip()

    def get_phone(self):
        return self.phone_input.text().strip()

    def get_address(self):
        return self.address_input.text().strip()

    def get_guest_data(self):
        return {
            'guest_id': self.get_guest_id(),
            'first_name': self.get_first_name(),
            'last_name': self.get_last_name(),
            'email': self.get_email(),
            'phone': self.get_phone(),
            'address': self.get_address()
        }

    def validate_inputs(self):
        if not self.get_first_name():
            QMessageBox.warning(self, "Error", "Please enter first name.")
            return False
        if not self.get_last_name():
            QMessageBox.warning(self, "Error", "Please enter last name.")
            return False
        if not self.get_email():
            QMessageBox.warning(self, "Error", "Please enter email.")
            return False
        if not self.get_phone():
            QMessageBox.warning(self, "Error", "Please enter contact number.")
            return False
        if not self.get_address():
            QMessageBox.warning(self, "Error", "Please enter address.")
            return False
        return True

    def accept(self):
        if self.validate_inputs():
            super().accept()


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = EditGuestView()
    dlg.load_guest_data("1", "John", "Doe", "john@example.com", "09123456789", "123 Main St")
    dlg.show()
    sys.exit(app.exec())