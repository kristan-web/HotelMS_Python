import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QSizePolicy, QApplication
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QCursor
from datetime import date, timedelta
import calendar


class DatePickerDialog(QDialog):
    """
    A reusable modal date picker dialog.
    Usage:
        chosen = DatePickerDialog.show_dialog(parent, "Pick a Date", date.today())
    Returns a datetime.date or None if cancelled.
    """

    # ── Colors ──────────────────────────────────────────────────────────────
    COL_BG          = "#2F2038"
    COL_HEADER      = "#FFE0E3"
    COL_HEADER_TEXT = "#2F2038"
    COL_TODAY       = "#BE3455"
    COL_SELECTED    = "#7B4F9E"
    COL_HOVER       = "#5A3D6B"
    COL_DAY_TEXT    = "#F2F2F2"
    COL_MUTED       = "#A797A5"
    COL_BTN_NAV     = "#412B4E"
    COL_BORDER      = "#412B4E"

    def __init__(self, parent=None, title: str = "Select Date",
                 initial: date = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(340, 360)
        self.selected_date = None
        self._displayed_month = (initial or date.today()).replace(day=1)
        self._build_ui()
        self._refresh()

    # ── UI SETUP ────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.COL_BG};
                border: 1px solid {self.COL_BORDER};
            }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        # ── HEADER ─────────────────────────────────────────────────────────
        header = QWidget()
        header.setObjectName("dp_header")
        header.setStyleSheet(f"""
            QWidget#dp_header {{
                background-color: {self.COL_HEADER};
                border-radius: 6px;
            }}
        """)
        header.setFixedHeight(44)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(6)

        self._prev_btn = self._nav_button("◀")
        self._prev_btn.clicked.connect(self._prev_month)

        self._month_label = QLabel()
        self._month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._month_label.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
        self._month_label.setStyleSheet(
            f"color: {self.COL_HEADER_TEXT}; background: transparent;")

        self._next_btn = self._nav_button("▶")
        self._next_btn.clicked.connect(self._next_month)

        header_layout.addWidget(self._prev_btn)
        header_layout.addWidget(self._month_label, stretch=1)
        header_layout.addWidget(self._next_btn)

        root.addWidget(header)

        # ── DAY OF WEEK ROW ────────────────────────────────────────────────
        dow_row = QWidget()
        dow_row.setStyleSheet("background: transparent;")
        dow_layout = QGridLayout(dow_row)
        dow_layout.setContentsMargins(0, 0, 0, 0)
        dow_layout.setSpacing(2)

        for col, day in enumerate(["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]):
            lbl = QLabel(day)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
            lbl.setStyleSheet(f"color: {self.COL_MUTED}; background: transparent;")
            dow_layout.addWidget(lbl, 0, col)

        root.addWidget(dow_row)

        # ── CALENDAR GRID ──────────────────────────────────────────────────
        self._grid_widget = QWidget()
        self._grid_widget.setStyleSheet("background: transparent;")
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(3)

        root.addWidget(self._grid_widget, stretch=1)

        # ── FOOTER ─────────────────────────────────────────────────────────
        footer = QHBoxLayout()
        footer.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        cancel_btn.setFixedSize(80, 30)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COL_BTN_NAV};
                color: {self.COL_HEADER};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        cancel_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        cancel_btn.clicked.connect(self.reject)
        footer.addWidget(cancel_btn)

        root.addLayout(footer)

    def _nav_button(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(30, 30)
        btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.COL_BTN_NAV};
                color: {self.COL_HEADER_TEXT};
                border: none;
                border-radius: 4px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; color: #FFE0E3; }}
        """)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return btn

    # ── NAVIGATION ──────────────────────────────────────────────────────────
    def _prev_month(self):
        m = self._displayed_month
        if m.month == 1:
            self._displayed_month = m.replace(year=m.year - 1, month=12)
        else:
            self._displayed_month = m.replace(month=m.month - 1)
        self._refresh()

    def _next_month(self):
        m = self._displayed_month
        if m.month == 12:
            self._displayed_month = m.replace(year=m.year + 1, month=1)
        else:
            self._displayed_month = m.replace(month=m.month + 1)
        self._refresh()

    # ── REFRESH CALENDAR ────────────────────────────────────────────────────
    def _refresh(self):
        # Update month/year label
        self._month_label.setText(
            self._displayed_month.strftime("%B %Y"))

        # Clear grid
        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        today        = date.today()
        first_dow    = self._displayed_month.weekday()  # Mon=0
        # Convert Monday-based to Sunday-based
        first_col    = (first_dow + 1) % 7
        days_in_month = calendar.monthrange(
            self._displayed_month.year, self._displayed_month.month)[1]

        # Fill empty cells before day 1
        for i in range(first_col):
            self._grid_layout.addWidget(QLabel(""), 0, i)

        col = first_col
        row = 0
        for day in range(1, days_in_month + 1):
            current = self._displayed_month.replace(day=day)
            btn = QPushButton(str(day))
            btn.setFixedSize(36, 36)
            btn.setFont(QFont("Segoe UI Semilight", 10))
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

            if current == self.selected_date:
                style = f"""
                    QPushButton {{
                        background-color: {self.COL_SELECTED};
                        color: #F2F2F2;
                        border: none;
                        border-radius: 18px;
                        font-weight: bold;
                    }}
                """
            elif current == today:
                style = f"""
                    QPushButton {{
                        background-color: {self.COL_TODAY};
                        color: #F2F2F2;
                        border: none;
                        border-radius: 18px;
                        font-weight: bold;
                    }}
                """
            else:
                style = f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {self.COL_DAY_TEXT};
                        border: none;
                        border-radius: 18px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.COL_HOVER};
                        color: #FFE0E3;
                    }}
                """

            btn.setStyleSheet(style)
            btn.clicked.connect(lambda _, d=current: self._select_date(d))
            self._grid_layout.addWidget(btn, row, col)

            col += 1
            if col == 7:
                col = 0
                row += 1

    def _select_date(self, chosen: date):
        self.selected_date = chosen
        self.accept()

    # ── STATIC HELPER ───────────────────────────────────────────────────────
    @staticmethod
    def show_dialog(parent=None, title: str = "Select Date",
                    initial: date = None) -> date | None:
        """Show the dialog and return chosen date, or None if cancelled."""
        dialog = DatePickerDialog(parent, title, initial)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_date
        return None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Test it
    from datetime import date
    result = DatePickerDialog.show_dialog(None, "Pick a Date", date.today())
    if result:
        print(f"Selected: {result}")
    else:
        print("Cancelled")

    sys.exit(0)