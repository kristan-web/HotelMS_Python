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

# Import dialog views
from views.GuestManagement.AddGuestView import AddGuestView
from views.GuestManagement.EditGuestView import EditGuestView


class GuestView(QWidget):
    # Signal definitions for controller communication
    add_requested = pyqtSignal(dict)
    edit_requested = pyqtSignal(dict)
    delete_requested = pyqtSignal(str)  # guest_id
    back_requested = pyqtSignal()

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Guest Management")
        self.setMinimumSize(900, 650)
        self.guests_data = []
        self.all_guests = []
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("guest_root")
        self.setStyleSheet(
            "QWidget#guest_root { background-color: #2F2038; border: none; }")

        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(10)

        # ── TITLE ROW ──────────────────────────────────────────────────────
        title_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title_lbl = QLabel("Guest Management")
        title_lbl.setFont(QFont("Segoe UI Semilight", 24, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")

        sub_lbl = QLabel("Manage your guest database")
        sub_lbl.setFont(QFont("Segoe UI Semilight", 14))
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
        self.add_btn.clicked.connect(self.open_add_guest)
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
        table_panel.setObjectName("guest_table_panel")
        table_panel.setStyleSheet("""
            QWidget#guest_table_panel {
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
        self.search_input.setPlaceholderText("🔍  Search guests...")
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
        self.search_input.textChanged.connect(self.search_guests)
        panel_layout.addWidget(self.search_input)

        # Table — 7 columns including Actions
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Guest ID", "First Name", "Last Name",
            "Contact", "Email", "Address", "Actions"
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
        self.table.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 160)
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

        self.deleted_btn = QPushButton("View Deleted Guests")
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
        self.deleted_btn.clicked.connect(self.view_deleted_guests)

        btn_row.addWidget(self.back_btn)
        btn_row.addWidget(self.deleted_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

    # ── NAVIGATION METHODS ─────────────────────────────────────────────────
    def go_back(self):
        """Navigate back to main window"""
        self.back_requested.emit()
        self.close()

    def view_deleted_guests(self):
        """Open deleted guests view"""
        from views.GuestManagement.DeletedGuestView import DeletedGuestsView
        self.deleted_view = DeletedGuestsView(self.main_window)
        self.deleted_view.show()
        self.hide()

    def open_add_guest(self):
        """Open add guest dialog"""
        self.add_dialog = AddGuestView(self)
        if self.add_dialog.exec():
            guest_data = {
                'first_name': self.add_dialog.get_first_name(),
                'last_name': self.add_dialog.get_last_name(),
                'email': self.add_dialog.get_email(),
                'phone': self.add_dialog.get_phone(),
                'address': self.add_dialog.get_address()
            }
            self.add_requested.emit(guest_data)

    def open_edit_guest(self, row):
        """Open edit guest dialog with selected guest data"""
        guest_id = self.get_table_value(row, 0)
        first_name = self.get_table_value(row, 1)
        last_name = self.get_table_value(row, 2)
        phone = self.get_table_value(row, 3)
        email = self.get_table_value(row, 4)
        address = self.get_table_value(row, 5)
        
        self.edit_dialog = EditGuestView(self)
        self.edit_dialog.load_guest_data(
            guest_id, first_name, last_name, email, phone, address
        )
        
        if self.edit_dialog.exec():
            updated_data = self.edit_dialog.get_guest_data()
            self.edit_requested.emit(updated_data)

    # ── ACTION BUTTONS PER ROW ───────────────────────────────────────────────
    def _make_row_buttons(self, row: int):
        """Creates Edit + Delete buttons for each table row."""
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
        edit_btn.clicked.connect(lambda _, r=row: self.open_edit_guest(r))

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
        del_btn.clicked.connect(lambda _, r=row: self.confirm_and_delete(r))

        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)

        return cell_widget, edit_btn, del_btn

    def confirm_and_delete(self, row):
        """Confirm and emit delete signal"""
        guest_name = f"{self.get_table_value(row, 1)} {self.get_table_value(row, 2)}"
        if self.confirm_delete(guest_name):
            guest_id = self.get_table_value(row, 0)
            self.delete_requested.emit(guest_id)

    def search_guests(self):
        """Filter guests based on search text"""
        search_text = self.get_search_text().lower()
        if hasattr(self, 'all_guests'):
            if not search_text:
                self.load_table(self.all_guests)
            else:
                filtered = [g for g in self.all_guests 
                           if search_text in g.get('first_name', '').lower() or 
                              search_text in g.get('last_name', '').lower() or
                              search_text in g.get('email', '').lower() or
                              search_text in g.get('phone', '').lower()]
                self.load_table(filtered)

    # ── PUBLIC METHODS ───────────────────────────────────────────────────────
    def load_table(self, guests: list):
        """Load guests into table"""
        self.all_guests = guests
        self.table.setRowCount(0)
        for g in guests:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)

            for col, key in enumerate(
                    ["guest_id", "first_name", "last_name", "phone", "email", "address"]):
                item = QTableWidgetItem(str(g.get(key, "")))
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, col, item)

            # Actions column
            cell, edit_btn, del_btn = self._make_row_buttons(row)
            self.table.setCellWidget(row, 6, cell)

    def load_sample_data(self):
        """Load sample data for testing"""
        sample_guests = [
            {"guest_id": "1", "first_name": "John", "last_name": "Doe",
             "phone": "09123456789", "email": "john@example.com", "address": "123 Main St"},
            {"guest_id": "2", "first_name": "Jane", "last_name": "Smith",
             "phone": "09876543210", "email": "jane@example.com", "address": "456 Oak Ave"},
        ]
        self.load_table(sample_guests)

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
            f'Delete guest "{name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = GuestView()
    w.load_sample_data()
    w.show()
    sys.exit(app.exec())