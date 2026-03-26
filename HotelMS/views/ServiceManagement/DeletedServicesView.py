# views/ServiceManagement/DeletedServicesView.py (MODIFIED)
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QSizePolicy, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

from controllers.service_controller import get_service_controller


class DeletedServicesView(QWidget):
    """View for managing deleted services with restore functionality."""
    
    deleted_data_changed = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.controller = get_service_controller()
        self.setWindowTitle("Deleted Services")
        self.setMinimumSize(900, 600)
        self._build_ui()
        self.load_deleted_services()
        
        # Connect search
        self.search_input.textChanged.connect(self.on_search)
    
    def _build_ui(self):
        self.setObjectName("del_root")
        self.setStyleSheet(
            "QWidget#del_root { background-color: #2F2038; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)

        # ── TITLE ROW ──────────────────────────────────────────────────────
        title_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title_lbl = QLabel("Deleted Services")
        title_lbl.setFont(QFont("Segoe UI Semilight", 20, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")

        sub_lbl = QLabel("List of deleted services")
        sub_lbl.setFont(QFont("Segoe UI Semilight", 11))
        sub_lbl.setStyleSheet("color: #A797A5; background: transparent;")

        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)

        title_row.addLayout(title_col)
        title_row.addStretch()

        self.restore_btn = QPushButton("Restore Service")
        self.restore_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.restore_btn.setFixedHeight(42)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.restore_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.restore_btn.clicked.connect(self.restore_service)
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
        table_panel.setObjectName("del_table_panel")
        table_panel.setStyleSheet("""
            QWidget#del_table_panel {
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
        self.search_input.setPlaceholderText("🔍  Search deleted services...")
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
            QLineEdit:focus { border: 1px solid #BE3455; }
        """)
        panel_layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Service ID", "Service Name", "Service Price",
            "Duration (mins.)", "Status"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setFont(QFont("Segoe UI Semilight", 11))
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(True)
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.setShowGrid(True)
        self.table.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
                padding: 6px;
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
            QPushButton:hover { background-color: #5A3D6B; }
        """)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.clicked.connect(self.go_back)

        btn_row.addWidget(self.back_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)
    
    # ── DATA LOADING ───────────────────────────────────────────────────────
    def load_deleted_services(self):
        """Load deleted services from database."""
        services = self.controller.get_all_deleted()
        self._populate_table(services)
    
    def _populate_table(self, services: list):
        """Populate table with deleted service data."""
        self.table.setRowCount(0)
        
        for service in services:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)
            
            # Set data in hidden column
            self.table.setItem(row, 0, QTableWidgetItem(str(service['id'])))
            
            # Service Name
            name_item = QTableWidgetItem(service['name'])
            name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 1, name_item)
            
            # Price
            price_item = QTableWidgetItem(f"₱{service['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 2, price_item)
            
            # Duration
            dur_item = QTableWidgetItem(str(service['duration']))
            dur_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 3, dur_item)
            
            # Status
            status_item = QTableWidgetItem(service['status'])
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 4, status_item)
    
    # ── SEARCH ─────────────────────────────────────────────────────────────
    def on_search(self, text: str):
        """Filter deleted services based on search text."""
        all_deleted = self.controller.get_all_deleted()
        if not text:
            self._populate_table(all_deleted)
        else:
            text_lower = text.lower()
            filtered = [s for s in all_deleted if text_lower in s['name'].lower()]
            self._populate_table(filtered)
    
    # ── RESTORE OPERATION ──────────────────────────────────────────────────
    def restore_service(self):
        """Restore selected service."""
        row = self.get_selected_row()
        if row >= 0:
            service_id = int(self.table.item(row, 0).text())
            service_name = self.table.item(row, 1).text()
            
            reply = QMessageBox.question(
                self, "Confirm Restore",
                f'Restore service "{service_name}"?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = self.controller.restore(service_id)
                
                if success:
                    QMessageBox.information(self, "Success", message)
                    self.load_deleted_services()
                    self.deleted_data_changed.emit()
                else:
                    QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.warning(self, "No Selection", "Please select a service to restore.")
    
    # ── NAVIGATION ─────────────────────────────────────────────────────────
    def go_back(self):
        """Navigate back to service management view."""
        from views.ServiceManagement.ServiceView import ServiceView
        self.service_view = ServiceView(self.main_window)
        self.service_view.show()
        self.close()
    
    # ── HELPERS ────────────────────────────────────────────────────────────
    def get_selected_row(self) -> int:
        return self.table.currentRow()
    
    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = DeletedServicesView()
    w.show()
    sys.exit(app.exec())