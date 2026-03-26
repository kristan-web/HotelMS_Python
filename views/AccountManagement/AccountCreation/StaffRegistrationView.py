import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QPixmap


def load_icon(path: str, w: int, h: int) -> QPixmap:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    px = QPixmap(os.path.join(base, path))
    if px.isNull():
        return QPixmap()
    return px.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)


class StaffRegistrationView(QWidget):
    """
    Staff Registration View.
    Split-panel form for registering new staff accounts.
    """
    
    # Signal definitions for controller communication
    registration_requested = pyqtSignal(dict)  # user data dict
    back_requested = pyqtSignal()
    
    def __init__(self, main_window=None, source="dashboard"):
        super().__init__()
        self.main_window = main_window
        self.source = source
        self.setWindowTitle("Staff Registration — Hotel MS")
        self.setMinimumSize(1000, 650)
        self._build_ui()
        self._load_icons()
    
    def _load_icons(self):
        self.logo_lbl.setPixmap(load_icon("resources/admin_logo.jpg", 350, 350))
    
    def _build_ui(self):
        self.setObjectName("root")
        self.setStyleSheet("QWidget#root { background-color: #FFE0E3; }")
        
        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        
        main.addWidget(self._build_form_panel(), stretch=3)
        main.addWidget(self._build_branding_panel(), stretch=2)
    
    def _build_form_panel(self):
        panel = QWidget()
        panel.setObjectName("form_panel")
        panel.setStyleSheet(
            "QWidget#form_panel { background-color: #2F2038; border: none; }")
        panel.setMinimumSize(550, 650)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Staff Registration")
        title.setFont(QFont("Segoe UI Semilight", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFE0E3; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Form fields container
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Row 1: First Name | Last Name
        row1 = QHBoxLayout()
        row1.setSpacing(20)
        
        first_name_col = QVBoxLayout()
        first_name_lbl = QLabel("First Name:")
        first_name_lbl.setFont(QFont("Segoe UI Semilight", 11))
        first_name_lbl.setStyleSheet("color: #FFE0E3;")
        self.first_name_input = self._make_input()
        first_name_col.addWidget(first_name_lbl)
        first_name_col.addWidget(self.first_name_input)
        
        last_name_col = QVBoxLayout()
        last_name_lbl = QLabel("Last Name:")
        last_name_lbl.setFont(QFont("Segoe UI Semilight", 11))
        last_name_lbl.setStyleSheet("color: #FFE0E3;")
        self.last_name_input = self._make_input()
        last_name_col.addWidget(last_name_lbl)
        last_name_col.addWidget(self.last_name_input)
        
        row1.addLayout(first_name_col)
        row1.addLayout(last_name_col)
        form_layout.addLayout(row1)
        
        # Email
        email_lbl = QLabel("Email Address:")
        email_lbl.setFont(QFont("Segoe UI Semilight", 11))
        email_lbl.setStyleSheet("color: #FFE0E3;")
        self.email_input = self._make_input()
        form_layout.addWidget(email_lbl)
        form_layout.addWidget(self.email_input)
        
        # Phone
        phone_lbl = QLabel("Contact Number:")
        phone_lbl.setFont(QFont("Segoe UI Semilight", 11))
        phone_lbl.setStyleSheet("color: #FFE0E3;")
        self.phone_input = self._make_input()
        form_layout.addWidget(phone_lbl)
        form_layout.addWidget(self.phone_input)
        
        # Row 2: Password | Confirm Password
        row2 = QHBoxLayout()
        row2.setSpacing(20)
        
        password_col = QVBoxLayout()
        password_lbl = QLabel("Password:")
        password_lbl.setFont(QFont("Segoe UI Semilight", 11))
        password_lbl.setStyleSheet("color: #FFE0E3;")
        self.password_input = self._make_input(password=True)
        password_col.addWidget(password_lbl)
        password_col.addWidget(self.password_input)
        
        confirm_col = QVBoxLayout()
        confirm_lbl = QLabel("Confirm Password:")
        confirm_lbl.setFont(QFont("Segoe UI Semilight", 11))
        confirm_lbl.setStyleSheet("color: #FFE0E3;")
        self.confirm_input = self._make_input(password=True)
        confirm_col.addWidget(confirm_lbl)
        confirm_col.addWidget(self.confirm_input)
        
        row2.addLayout(password_col)
        row2.addLayout(confirm_col)
        form_layout.addLayout(row2)
        
        layout.addWidget(form_widget)
        layout.addSpacing(30)
        
        # Buttons row (Back + Register)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(15)
        
        # Back button
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
        self.back_btn.setFixedHeight(42)
        self.back_btn.setMinimumWidth(120)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #5A3D6B;
            }
        """)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.clicked.connect(self.go_back)
        
        # Register Button
        self.register_btn = QPushButton("Register")
        self.register_btn.setFont(QFont("Segoe UI Semilight", 14, QFont.Weight.Bold))
        self.register_btn.setFixedHeight(48)
        self.register_btn.setMinimumWidth(200)
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #A02848;
            }
        """)
        self.register_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.register_btn.clicked.connect(self.handle_registration)
        
        btn_row.addWidget(self.back_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.register_btn)
        layout.addLayout(btn_row)
        
        layout.addStretch()
        
        return panel
    
    def _build_branding_panel(self):
        panel = QWidget()
        panel.setObjectName("brand_panel")
        panel.setStyleSheet(
            "QWidget#brand_panel { background-color: #FFE0E3; border: none; }")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(40, 60, 40, 60)
        layout.setSpacing(12)
        
        title = QLabel("Hotel MS")
        title.setFont(QFont("Segoe UI Semilight", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #2F2038; border: none;")
        layout.addWidget(sep)
        
        sub = QLabel("Registration Form for Staffs.")
        sub.setFont(QFont("Segoe UI Semilight", 12))
        sub.setStyleSheet("color: #2F2038; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)
        
        layout.addSpacing(30)
        
        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(240, 240)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(self.logo_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        layout.addStretch()
        
        return panel
    
    def _make_input(self, password=False) -> QLineEdit:
        field = QLineEdit()
        field.setFont(QFont("Segoe UI Semilight", 11))
        field.setFixedHeight(34)
        if password:
            field.setEchoMode(QLineEdit.EchoMode.Password)
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
    
    def go_back(self):
        """Emit signal to go back"""
        self.back_requested.emit()
        self.close()
    
    def handle_registration(self):
        """Validate inputs and emit registration signal"""
        user_data = {
            'first_name': self.get_first_name(),
            'last_name': self.get_last_name(),
            'email': self.get_email(),
            'phone': self.get_phone(),
            'password': self.get_password(),
            'role': 'Staff'
        }
        
        # Validation
        if not user_data['first_name']:
            self.show_error("Please enter first name.")
            return
        if not user_data['last_name']:
            self.show_error("Please enter last name.")
            return
        if not user_data['email']:
            self.show_error("Please enter email address.")
            return
        if not user_data['phone']:
            self.show_error("Please enter contact number.")
            return
        if not user_data['password']:
            self.show_error("Please enter password.")
            return
        if user_data['password'] != self.get_confirm():
            self.show_error("Passwords do not match.")
            return
        if len(user_data['password']) < 6:
            self.show_error("Password must be at least 6 characters.")
            return
        
        self.registration_requested.emit(user_data)
    
    # ── Getters ──────────────────────────────────────────────────────────────
    def get_first_name(self):
        return self.first_name_input.text().strip()
    
    def get_last_name(self):
        return self.last_name_input.text().strip()
    
    def get_email(self):
        return self.email_input.text().strip()
    
    def get_phone(self):
        return self.phone_input.text().strip()
    
    def get_password(self):
        return self.password_input.text()
    
    def get_confirm(self):
        return self.confirm_input.text()
    
    def show_message(self, title: str, msg: str):
        QMessageBox.information(self, title, msg)
    
    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    w = StaffRegistrationView()
    w.show()
    sys.exit(app.exec())