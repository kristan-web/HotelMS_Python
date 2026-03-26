# views/ServiceManagement/AddServiceView.py (MODIFIED)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QLineEdit, QPushButton,
    QComboBox, QVBoxLayout, QHBoxLayout, QSizePolicy,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

from controllers.service_controller import get_service_controller


class AddServiceView(QDialog):
    """Dialog for adding a new service with controller integration."""
    
    service_added = pyqtSignal(dict)  # Signal when service is added
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = get_service_controller()
        self.setWindowTitle("Add New Service")
        self.setModal(True)
        self.setFixedSize(520, 400)
        self._build_ui()
        self._connect_signals()
    
    def _build_ui(self):
        self.setStyleSheet("background-color: #2F2038;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── HEADER ─────────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("add_header")
        header.setStyleSheet(
            "QWidget#add_header { background-color: #FFE0E3; border: none; }")
        header.setFixedHeight(48)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)

        title = QLabel("Add New Service")
        title.setFont(QFont("Segoe UI Semilight", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038; background: transparent;")
        header_layout.addWidget(title)

        root.addWidget(header)

        # ── FORM BODY ──────────────────────────────────────────────────────
        body = QWidget()
        body.setObjectName("add_body")
        body.setStyleSheet("QWidget#add_body { background-color: #2F2038; border: none; }")

        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 20, 20, 20)
        body_layout.setSpacing(12)

        # Row 1: Service Name | Service Price
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        name_col = QVBoxLayout()
        name_col.setSpacing(4)
        name_lbl = QLabel("Service Name")
        name_lbl.setFont(QFont("Segoe UI Semilight", 11))
        name_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        self.service_name_input = self._make_input()
        name_col.addWidget(name_lbl)
        name_col.addWidget(self.service_name_input)

        price_col = QVBoxLayout()
        price_col.setSpacing(4)
        price_lbl = QLabel("Service Price: *")
        price_lbl.setFont(QFont("Segoe UI Semilight", 11))
        price_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        self.service_price_input = self._make_input()
        price_col.addWidget(price_lbl)
        price_col.addWidget(self.service_price_input)

        row1.addLayout(name_col, stretch=1)
        row1.addLayout(price_col, stretch=1)
        body_layout.addLayout(row1)

        # Duration
        dur_lbl = QLabel("Service Duration (in mins.): *")
        dur_lbl.setFont(QFont("Segoe UI Semilight", 11))
        dur_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        self.service_duration_input = self._make_input()
        body_layout.addWidget(dur_lbl)
        body_layout.addWidget(self.service_duration_input)

        # Status
        status_lbl = QLabel("Status: *")
        status_lbl.setFont(QFont("Segoe UI Semilight", 11))
        status_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        self.service_status_input = QComboBox()
        self.service_status_input.addItems(["Active", "Inactive", "Maintenance"])
        self.service_status_input.setFont(QFont("Segoe UI Semilight", 11))
        self.service_status_input.setFixedHeight(34)
        self.service_status_input.setStyleSheet("""
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
        body_layout.addWidget(status_lbl)
        body_layout.addWidget(self.service_status_input)

        body_layout.addStretch()

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.save_btn = self._make_button("Save", "#BE3455", "#FFE0E3")
        self.cancel_btn = self._make_button("Cancel", "#FFE0E3", "#2F2038")
        self.cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        body_layout.addLayout(btn_row)

        root.addWidget(body, stretch=1)
    
    def _connect_signals(self):
        """Connect button signals."""
        self.save_btn.clicked.connect(self.handle_save)
    
    def handle_save(self):
        """Validate and save the service."""
        name = self.get_service_name()
        price = self.get_service_price()
        duration = self.get_service_duration()
        status = self.get_service_status()
        
        # Validation
        if not name:
            QMessageBox.warning(self, "Validation Error", "Service name is required.")
            return
        
        if not price:
            QMessageBox.warning(self, "Validation Error", "Service price is required.")
            return
        
        if not duration:
            QMessageBox.warning(self, "Validation Error", "Service duration is required.")
            return
        
        # Call controller
        success, message = self.controller.create(name, price, duration, status)
        
        if success:
            # Emit signal with the new service data
            self.service_added.emit({
                'name': name,
                'price': float(price),
                'duration': int(duration),
                'status': status
            })
            QMessageBox.information(self, "Success", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)

    # ── HELPERS ──────────────────────────────────────────────────────────────
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
            QPushButton:hover {{ opacity: 0.85; }}
        """)
        return btn

    # ── PUBLIC GETTERS ───────────────────────────────────────────────────────
    def get_service_name(self) -> str:
        return self.service_name_input.text().strip()

    def get_service_price(self) -> str:
        return self.service_price_input.text().strip()

    def get_service_duration(self) -> str:
        return self.service_duration_input.text().strip()

    def get_service_status(self) -> str:
        return self.service_status_input.currentText()

    def set_service_data(self, name: str, price: str,
                         duration: str, status: str):
        self.service_name_input.setText(name)
        self.service_price_input.setText(price)
        self.service_duration_input.setText(duration)
        self.service_status_input.setCurrentText(status)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dlg = AddServiceView()
    dlg.show()
    sys.exit(app.exec())