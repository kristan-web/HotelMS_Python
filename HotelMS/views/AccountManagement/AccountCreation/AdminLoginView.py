import sys
import os
from controllers.auth_controller import get_auth_controller
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap


def load_icon(path: str, w: int, h: int) -> QPixmap:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    px = QPixmap(os.path.join(base, path))
    if px.isNull():
        return QPixmap()
    return px.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)


class AdminLoginView(QWidget):
    """
    Split-panel Admin Login screen.
    Left = pink branding panel | Right = dark purple login form
    Navigation signals (wire in controller):
        self.login_btn       → authenticate admin
        self.staff_btn       → open StaffLoginView
        self.forgot_lbl      → open ForgotPasswordView
    """
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Admin Login — Hotel MS")
        self.setMinimumSize(1000, 650)
        self._build_ui()
        self._load_icons()

    def _load_icons(self):
        self.logo_lbl.setPixmap(load_icon("resources/admin_logo.jpg", 350, 350))

    def _build_ui(self):
        self.setObjectName("root")
        self.setStyleSheet("QWidget#root { background-color: #FFE0E3; border: none; }")

        main = QHBoxLayout(self)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        main.addWidget(self._build_left_panel(), stretch=2)
        main.addWidget(self._build_right_panel(), stretch=3)

    # ── LEFT BRANDING PANEL ──────────────────────────────────────────────────
    def _build_left_panel(self):
        panel = QWidget()
        panel.setObjectName("left_panel")
        panel.setStyleSheet(
            "QWidget#left_panel { background-color: #FFE0E3; border: none; }")

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

        sub = QLabel("Welcome to Hotel Management System")
        sub.setFont(QFont("Segoe UI Semilight", 12))
        sub.setStyleSheet("color: #2F2038; background: transparent;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(30)

        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(350, 350)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setStyleSheet("background: transparent;")
        layout.addWidget(self.logo_lbl, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch()

        return panel

    # ── RIGHT LOGIN FORM PANEL ───────────────────────────────────────────────
    def _build_right_panel(self):
        panel = QWidget()
        panel.setObjectName("right_panel")
        panel.setStyleSheet(
            "QWidget#right_panel { background-color: #2F2038; border: none; }")
        panel.setMinimumWidth(530)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(90, 80, 90, 80)
        layout.setSpacing(0)

        # Title
        title = QLabel("Admin Login")
        title.setFont(QFont("Segoe UI Semilight", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFE0E3; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        layout.addSpacing(40)

        # Email
        email_lbl = QLabel("Email:")
        email_lbl.setFont(QFont("Segoe UI Semilight", 12))
        email_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        layout.addWidget(email_lbl)
        layout.addSpacing(4)

        self.email_input = self._make_input()
        layout.addWidget(self.email_input)
        layout.addSpacing(18)

        # Password
        pass_lbl = QLabel("Password:")
        pass_lbl.setFont(QFont("Segoe UI Semilight", 12))
        pass_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        layout.addWidget(pass_lbl)
        layout.addSpacing(4)

        self.password_input = self._make_input(password=True)
        layout.addWidget(self.password_input)
        layout.addSpacing(50)

        # Login button
        self.login_btn = QPushButton("Login")
        self.login_btn.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        self.login_btn.setFixedHeight(42)
        self.login_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFE0DB;
                color: #2F2038;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #F0C8C0; }
        """)
        self.login_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)
        layout.addSpacing(6)

        # Forgot Password
        self.forgot_lbl = QLabel("Forgot Password?")
        self.forgot_lbl.setFont(QFont("Segoe UI Semilight", 12))
        self.forgot_lbl.setStyleSheet(
            "color: #FFE0E3; background: transparent;")
        self.forgot_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.forgot_lbl.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.forgot_lbl.mousePressEvent = self.open_forgot_password
        layout.addWidget(self.forgot_lbl)

        layout.addStretch()

        # Switch to Staff
        self.staff_btn = QPushButton("Staff")
        self.staff_btn.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
        self.staff_btn.setFixedSize(86, 42)
        self.staff_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.staff_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.staff_btn.clicked.connect(self.open_staff_login)
        layout.addWidget(self.staff_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addSpacing(20)

        return panel

    def _make_input(self, password=False) -> QLineEdit:
        f = QLineEdit()
        f.setFont(QFont("Segoe UI Semilight", 12))
        f.setFixedHeight(34)
        if password:
            f.setEchoMode(QLineEdit.EchoMode.Password)
        f.setStyleSheet("""
            QLineEdit {
                background-color: #F9F5FF;
                color: #2F2038;
                border: 1px solid #A797A5;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QLineEdit:focus { border: 1px solid #BE3455; }
        """)
        return f

    # ── NAVIGATION METHODS ───────────────────────────────────────────────────
    # Replace the login method with this:
    def login(self):
        """Handle admin login with database authentication"""
        email = self.get_email()
        password = self.get_password()

        if not email:
            self.show_error("Please enter email address.")
            return
        if not password:
            self.show_error("Please enter password.")
            return

        # Authenticate using controller
        auth = get_auth_controller()
        success, message, user_data = auth.login_admin(email, password)

        if not success:
            self.show_error(message)
            return

        self.show_message("Success", message)

        # Navigate to admin dashboard
        from views.Dashboard.AdminDashboardView import AdminDashboardView
        self.dashboard = AdminDashboardView()

        # Set user info in dashboard
        if user_data:
            self.dashboard.set_session_label(f"{user_data['first_name']} {user_data['last_name']}")
            # Store user ID for later use
            self.dashboard.user_id = user_data['user_id']

        self.dashboard.show()
        self.close()


    def open_staff_login(self):
        """Open staff login view"""
        from views.AccountManagement.AccountCreation.StaffLoginView import StaffLoginView
        self.staff_login = StaffLoginView()  # Removed main_window argument
        self.staff_login.show()
        self.close()

    def open_forgot_password(self, event):
        """Open forgot password view"""
        from views.AccountManagement.AccountCreation.ForgotPasswordView import ForgotPasswordView
        self.forgot_view = ForgotPasswordView()  # Removed main_window argument
        self.forgot_view.show()
        self.close()

    # ── PUBLIC GETTERS ───────────────────────────────────────────────────────
    def get_email(self) -> str:
        return self.email_input.text().strip()

    def get_password(self) -> str:
        return self.password_input.text()

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Login Failed", msg)
    
    def show_message(self, title: str, msg: str):
        QMessageBox.information(self, title, msg)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = AdminLoginView()
    w.show()
    sys.exit(app.exec())