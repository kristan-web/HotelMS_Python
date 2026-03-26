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

class EnterOTPView(QDialog):
    """
    OTP entry dialog.
    Wire in controller: self.enter_btn
    """
    def __init__(self, source: str = "admin", parent=None):
        super().__init__(parent)
        self.source = source
        self.setWindowTitle("Enter OTP")
        self.setModal(True)
        self.setFixedSize(350, 225)
        self.setStyleSheet("background-color: #2F2038;")
        self._build_ui()
 
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(72, 49, 72, 20)
        layout.setSpacing(8)
 
        title = QLabel("Enter the code:")
        title.setFont(QFont("Segoe UI Semilight", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFE0E3; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
 
        layout.addSpacing(20)
 
        self.otp_input = QLineEdit()
        self.otp_input.setFont(QFont("Segoe UI Semilight", 14))
        self.otp_input.setFixedHeight(34)
        self.otp_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_input.setStyleSheet(_INPUT_STYLE)
        layout.addWidget(self.otp_input)
 
        layout.addSpacing(20)
 
        self.enter_btn = QPushButton("Enter")
        self.enter_btn.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
        self.enter_btn.setFixedHeight(35)
        self.enter_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.enter_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.enter_btn)
 
    def get_otp(self) -> str:
        return self.otp_input.text().strip()
 
    def clear(self):
        self.otp_input.clear()
 
    def show_error(self, msg: str):
        QMessageBox.warning(self, "Invalid OTP", msg)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # Test ForgotPasswordView
    w = EnterOTPView(source="admin")
    w.show()
    sys.exit(app.exec())