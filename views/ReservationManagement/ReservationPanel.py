import sys
import os
from datetime import date

# Ensure local imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
    QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSizePolicy, QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont, QCursor

# Importing from your provided DatePicker.py
from DatePicker import DatePickerDialog 

class ReservationPanel(QWidget):
    FMT = "%b %d, %Y"

    def __init__(self):
        super().__init__()
        self.check_in_date = None
        self.check_out_date = None
        self._build_ui()

    def _build_ui(self):
        self.setObjectName("res_root")
        self.setStyleSheet("QWidget#res_root { background-color: #2F2038; border: none; }")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        # ── TOP FORM PANEL (Booking Section) ───────────────────────────────
        root_layout.addWidget(self._build_booking_panel())

        # ── BOTTOM TABLE PANEL (Management Section) ────────────────────────
        root_layout.addWidget(self._build_table_panel(), stretch=1)

    def _build_booking_panel(self):
        form_outer = QFrame()
        form_outer.setObjectName("form_outer")
        form_outer.setStyleSheet("""
            QFrame#form_outer {
                background-color: #2F2038;
                border: 1px solid #412B4E;
                border-radius: 6px;
            }
        """)

        layout = QHBoxLayout(form_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Panel 1: Selection (Guest & Room)
        layout.addWidget(self._build_selection_sub_panel(), stretch=1)
        
        # Panel 2: Dates
        layout.addWidget(self._build_date_sub_panel(), stretch=1)

        # Panel 3: Confirmation & Total
        layout.addWidget(self._build_confirm_sub_panel(), stretch=1)

        return form_outer

    def _build_selection_sub_panel(self):
        panel = QFrame()
        panel.setObjectName("sub_panel")
        panel.setStyleSheet("QFrame#sub_panel { background-color: #3D2850; border-radius: 6px; }")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 14, 20, 14)
        
        # Label & Combo Style
        lbl_style = "color: #FFE0E3; background: transparent; font-size: 11pt;"
        combo_style = """
            QComboBox, QTextEdit { 
                background-color: #F9F5FF; color: #2F2038; 
                border-radius: 4px; padding: 2px 8px; 
            }
        """

        layout.addWidget(self._styled_label("Guest Name:", lbl_style))
        self.guest_combo = QComboBox()
        self.guest_combo.setStyleSheet(combo_style)
        layout.addWidget(self.guest_combo)

        layout.addWidget(self._styled_label("Select Room:", lbl_style))
        self.room_combo = QComboBox()
        self.room_combo.setStyleSheet(combo_style)
        layout.addWidget(self.room_combo)

        layout.addWidget(self._styled_label("Notes:", lbl_style))
        self.notes_area = QTextEdit()
        self.notes_area.setFixedHeight(45)
        self.notes_area.setStyleSheet(combo_style)
        layout.addWidget(self.notes_area)

        return panel

    def _build_date_sub_panel(self):
        panel = QFrame()
        panel.setObjectName("sub_panel")
        panel.setStyleSheet("QFrame#sub_panel { background-color: #3D2850; border-radius: 6px; }")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 14, 20, 14)
        
        lbl_style = "color: #FFE0E3; background: transparent; font-size: 11pt;"
        field_style = "background-color: #F9F5FF; color: #2F2038; border-radius: 4px; padding: 5px;"
        btn_pick_style = "background-color: #412B4E; color: #FFE0E3; border-radius: 4px; font-weight: bold;"

        # Check In
        layout.addWidget(self._styled_label("Check-In Date:", lbl_style))
        h1 = QHBoxLayout()
        self.check_in_field = QLineEdit()
        self.check_in_field.setReadOnly(True)
        self.check_in_field.setStyleSheet(field_style)
        btn_in = QPushButton("📅")
        btn_in.setFixedSize(35, 30)
        btn_in.setStyleSheet(btn_pick_style)
        btn_in.clicked.connect(self.handle_pick_check_in)
        h1.addWidget(self.check_in_field)
        h1.addWidget(btn_in)
        layout.addLayout(h1)

        # Check Out
        layout.addWidget(self._styled_label("Check-Out Date:", lbl_style))
        h2 = QHBoxLayout()
        self.check_out_field = QLineEdit()
        self.check_out_field.setReadOnly(True)
        self.check_out_field.setStyleSheet(field_style)
        btn_out = QPushButton("📅")
        btn_out.setFixedSize(35, 30)
        btn_out.setStyleSheet(btn_pick_style)
        btn_out.clicked.connect(self.handle_pick_check_out)
        h2.addWidget(self.check_out_field)
        h2.addWidget(btn_out)
        layout.addLayout(h2)

        return panel

    def _build_confirm_sub_panel(self):
        panel = QFrame()
        panel.setObjectName("sub_panel")
        panel.setStyleSheet("QFrame#sub_panel { background-color: #3D2850; border-radius: 6px; }")
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 14, 20, 14)

        self.btn_find_rooms = QPushButton("Find Available Rooms")
        self.btn_find_rooms.setFixedHeight(35)
        self.btn_find_rooms.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_find_rooms.setStyleSheet("""
            QPushButton { background-color: #412B4E; color: #FFE0E3; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #5A3D6B; }
        """)

        self.btn_confirm = QPushButton("Confirm Reservation")
        self.btn_confirm.setFixedHeight(35)
        self.btn_confirm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_confirm.setStyleSheet("""
            QPushButton { background-color: #FFE0E3; color: #2F2038; border-radius: 6px; font-weight: bold; }
            QPushButton:hover { background-color: #F0C8CC; }
        """)

        self.lbl_total = QLabel("Total: ₱0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setStyleSheet("color: #FFE0E3; font-size: 16pt; font-weight: bold; margin-top: 10px;")

        layout.addWidget(self.btn_find_rooms)
        layout.addWidget(self.btn_confirm)
        layout.addWidget(self.lbl_total)

        return panel

    def _build_table_panel(self):
        table_outer = QFrame()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet("""
            QFrame#table_outer {
                background-color: #2F2038;
                border: 1px solid #412B4E;
                border-radius: 6px;
            }
        """)

        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)

        # Filter and Action Row
        btn_row = QHBoxLayout()
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(["ALL", "CONFIRMED", "CHECKED_IN", "CHECKED_OUT", "CANCELLED"])
        self.status_filter.setFixedWidth(150)
        self.status_filter.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px;")

        btn_row.addWidget(self._styled_label("Filter Status:", "color: #FFE0E3;"))
        btn_row.addWidget(self.status_filter)
        btn_row.addSpacing(20)

        # Action Buttons
        self.btn_check_in = self._action_button("Check In", "#412B4E")
        self.btn_check_out = self._action_button("Check Out", "#412B4E")
        self.btn_cancel = self._action_button("Cancel", "#BE3455")
        self.btn_refresh = self._action_button("Refresh", "#412B4E")

        btn_row.addWidget(self.btn_check_in)
        btn_row.addWidget(self.btn_check_out)
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        
        layout.addLayout(btn_row)

        # Table (Using your GuestPanel Style)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Guest", "Room", "Check-In", "Check-Out", "Nights", "Total", "Status"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850; color: #F2F2F2;
                gridline-color: #412B4E; border-radius: 4px;
            }
            QHeaderView::section {
                background-color: #412B4E; color: #FFE0E3;
                font-weight: bold; border: none; padding: 6px;
            }
            QTableWidget::item:selected { background-color: #BE3455; color: #FFE0E3; }
        """)

        layout.addWidget(self.table)
        return table_outer

    # ── Helpers ────────────────────────────────────────────────────────────

    def _styled_label(self, text, style):
        lbl = QLabel(text)
        lbl.setStyleSheet(style)
        lbl.setFont(QFont("Segoe UI Semilight", 11))
        return lbl

    def _action_button(self, text, bg_color):
        btn = QPushButton(text)
        btn.setFixedSize(110, 34)
        btn.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: #FFE0E3;
                border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        return btn

    @pyqtSlot()
    def handle_pick_check_in(self):
        d = DatePickerDialog.show_dialog(self, "Check-In Date", date.today())
        if d:
            self.check_in_date = d
            self.check_in_field.setText(d.strftime(self.FMT))

    @pyqtSlot()
    def handle_pick_check_out(self):
        d = DatePickerDialog.show_dialog(self, "Check-Out Date", date.today())
        if d:
            self.check_out_date = d
            self.check_out_field.setText(d.strftime(self.FMT))

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ReservationPanel()
    w.resize(1200, 750)
    w.show()
    sys.exit(app.exec())