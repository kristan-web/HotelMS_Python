import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
 
from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor
 
 
# ── Shared styling helpers ────────────────────────────────────────────────────
_INPUT_STYLE = """
    QLineEdit {
        background-color: #F9F5FF;
        color: #2F2038;
        border: 1px solid #A797A5;
        border-radius: 4px;
        padding: 2px 8px;
    }
    QLineEdit:focus { border: 1px solid #BE3455; }
"""
 
_BTN_STYLE = """
    QPushButton {
        background-color: #2F2038;
        color: #FFE0E3;
        border: none;
        border-radius: 6px;
    }
    QPushButton:hover { background-color: #412B4E; }
"""
 
 
def _make_dialog(parent, title: str, w=380, h=230) -> 'QDialog':
    dlg = QDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setModal(True)
    dlg.setFixedSize(w, h)
    dlg.setStyleSheet("background-color: #2F2038;")
    return dlg

# ─────────────────────────────────────────────────────────────────────────────
# 1. ForgotPasswordView
# ─────────────────────────────────────────────────────────────────────────────
class ForgotPasswordView(QDialog):
    """
    Asks user for their email → sends OTP → opens EnterOTPView.
    Wire in controller: self.submit_btn
    """
    def __init__(self, source: str = "admin", parent=None):
        super().__init__(parent)
        self.source = source
        self.setWindowTitle("Forgot Password")
        self.setModal(True)
        self.setFixedSize(390, 240)
        self.setStyleSheet("background-color: #FFE0E3;")
        self._build_ui()
 
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 50, 20, 20)
        layout.setSpacing(8)
 
        title = QLabel("Enter your email:")
        title.setFont(QFont("Segoe UI Semilight", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038; background: transparent;")
        layout.addWidget(title)
 
        self.email_input = QLineEdit()
        self.email_input.setFont(QFont("Segoe UI Semilight", 12))
        self.email_input.setFixedHeight(34)
        self.email_input.setStyleSheet(_INPUT_STYLE.replace("#BE3455", "#2F2038"))
        layout.addWidget(self.email_input)
 
        hint = QLabel("A code will be sent to your email shortly.")
        hint.setFont(QFont("Segoe UI Semilight", 11))
        hint.setStyleSheet("color: #BE3455; background: transparent;")
        layout.addWidget(hint)
 
        layout.addSpacing(20)
 
        self.submit_btn = QPushButton("Submit")
        self.submit_btn.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
        self.submit_btn.setFixedHeight(38)
        self.submit_btn.setStyleSheet(_BTN_STYLE)
        self.submit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.submit_btn)
 
    def get_email(self) -> str:
        return self.email_input.text().strip()
 
    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Test ForgotPasswordView
    w = ForgotPasswordView(source="admin")
    w.show()
    sys.exit(app.exec())