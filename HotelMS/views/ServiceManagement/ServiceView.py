import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QAbstractItemView,
    QSizePolicy, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor

from views.ServiceManagement.AddServiceView import AddServiceView
from views.ServiceManagement.EditServiceView import EditServiceView


class ServiceView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Service Management")
        self.setMinimumSize(900, 650)
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("svc_root")
        self.setStyleSheet(
            "QWidget#svc_root { background-color: #2F2038; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)

        # ── TITLE ROW ──────────────────────────────────────────────────────
        title_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title_lbl = QLabel("Service Management")
        title_lbl.setFont(QFont("Segoe UI Semilight", 20, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")

        sub_lbl = QLabel("Manage your services here")
        sub_lbl.setFont(QFont("Segoe UI Semilight", 11))
        sub_lbl.setStyleSheet("color: #A797A5; background: transparent;")

        title_col.addWidget(title_lbl)
        title_col.addWidget(sub_lbl)

        title_row.addLayout(title_col)
        title_row.addStretch()

        self.add_btn = QPushButton("＋  Add")
        self.add_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.add_btn.setFixedHeight(42)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 20px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.add_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.add_btn.clicked.connect(self.open_add_service)
        title_row.addWidget(self.add_btn)

        root.addLayout(title_row)

        # ── SEPARATOR ──────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #412B4E; border: none;")
        root.addWidget(sep)

        # ── TABLE PANEL ────────────────────────────────────────────────────
        table_panel = QWidget()
        table_panel.setObjectName("svc_table_panel")
        table_panel.setStyleSheet("""
            QWidget#svc_table_panel {
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
        self.search_input.setPlaceholderText("🔍  Search services...")
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

        # Table — 6 columns including Actions
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Service ID", "Service Name", "Service Price",
            "Duration (mins.)", "Status", "Actions"
        ])
        self.table.setColumnHidden(0, True)
        self.table.setFont(QFont("Segoe UI Semilight", 11)) 
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(True)  # Show row numbers
        self.table.verticalHeader().setStyleSheet("background-color: #412B4E;")
        self.table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 160)
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

        self.deleted_btn = QPushButton("View Deleted Services")
        self.deleted_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.deleted_btn.setFixedHeight(42)
        self.deleted_btn.setStyleSheet("""
            QPushButton {
                background-color: #7B2D3E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.deleted_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.deleted_btn.clicked.connect(self.view_deleted_services)

        btn_row.addWidget(self.back_btn)
        btn_row.addWidget(self.deleted_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

    def go_back(self):
        if self.main_window:
            self.main_window.show()
        self.close()

    def view_deleted_services(self):
        from views.ServiceManagement.DeletedServicesView import DeletedServicesView
        self.deleted_view = DeletedServicesView(self.main_window)
        self.deleted_view.show()
        self.hide()

    def open_add_service(self):
        self.add_dialog = AddServiceView(self)
        if self.add_dialog.exec():
            service_data = {
                'name': self.add_dialog.get_service_name(),
                'price': self.add_dialog.get_service_price(),
                'duration': self.add_dialog.get_service_duration(),
                'status': self.add_dialog.get_service_status()
            }
            if hasattr(self, 'add_requested'):
                self.add_requested.emit(service_data)

    def _make_row_buttons(self, row: int):
        cell_widget = QWidget()
        cell_widget.setObjectName("row_btn_widget")
        cell_widget.setStyleSheet(
            "QWidget#row_btn_widget { background-color: #3D2850; border: none; }")

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
            QPushButton:hover { background-color: #5A3D6B; }
        """)
        edit_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        edit_btn.clicked.connect(lambda _, r=row: self.open_edit_service(r))

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
            QPushButton:hover { background-color: #A02848; }
        """)
        del_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)

        return cell_widget, edit_btn, del_btn

    def open_edit_service(self, row):
        service_id = self.get_table_value(row, 0)
        service_name = self.get_table_value(row, 1)
        service_price = self.get_table_value(row, 2)
        service_duration = self.get_table_value(row, 3)
        service_status = self.get_table_value(row, 4)
        
        self.edit_dialog = EditServiceView(self)
        self.edit_dialog.load_service_data(
            service_id, service_name, service_price, 
            service_duration, service_status
        )
        
        if self.edit_dialog.exec():
            updated_data = {
                'id': self.edit_dialog.get_service_id(),
                'name': self.edit_dialog.get_service_name(),
                'price': self.edit_dialog.get_service_price(),
                'duration': self.edit_dialog.get_service_duration(),
                'status': self.edit_dialog.get_service_status()
            }
            if hasattr(self, 'edit_requested'):
                self.edit_requested.emit(updated_data)

    def load_table(self, services: list,
                   on_edit=None, on_delete=None):
        self.table.setRowCount(0)
        for s in services:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)

            for col, key in enumerate(
                    ["id", "name", "price", "duration", "status"]):
                item = QTableWidgetItem(str(s.get(key, "")))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, col, item)

            cell, edit_btn, del_btn = self._make_row_buttons(row)
            if on_edit:
                edit_btn.clicked.disconnect()
                edit_btn.clicked.connect(lambda _, r=row: on_edit(r))
            if on_delete:
                del_btn.clicked.connect(lambda _, r=row: on_delete(r))
            self.table.setCellWidget(row, 5, cell)

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""

    def get_search_text(self) -> str:
        return self.search_input.text().strip()

    def show_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def confirm_delete(self, name: str) -> bool:
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f'Delete service "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ServiceView()
    w.load_table([
        {"id": 1, "name": "Massage Therapy", "price": "₱500",
         "duration": "60", "status": "Active"},
        {"id": 2, "name": "Facial Treatment", "price": "₱300",
         "duration": "45", "status": "Active"},
        {"id": 3, "name": "Body Scrub", "price": "₱400",
         "duration": "50", "status": "Inactive"},
    ])
    w.show()
    sys.exit(app.exec())