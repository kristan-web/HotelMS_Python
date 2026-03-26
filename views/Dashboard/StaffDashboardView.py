import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout,
    QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap


# ── Helper to load and scale an image ───────────────────────────────────────
def load_icon(relative_path: str, w: int, h: int) -> QPixmap:
    """Load an image from the resources folder relative to project root."""
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    full_path = os.path.join(base, relative_path)
    pixmap = QPixmap(full_path)
    if pixmap.isNull():
        return QPixmap()
    return pixmap.scaled(w, h,
                         Qt.AspectRatioMode.KeepAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)


class StaffDashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Staff Dashboard")
        self.setMinimumSize(900, 550)
        self._build_ui()
        self._load_icons()

    # ── ICON LOADING ────────────────────────────────────────────────────────
    def _load_icons(self):
        self.logo_label.setPixmap(load_icon("resources/admin_logo.jpg", 60, 50))
        self.icon_reservations.setPixmap(load_icon("resources/reserved.png",  40, 40))
        self.icon_checkins.setPixmap(    load_icon("resources/check.png",      35, 32))
        self.icon_revenue.setPixmap(     load_icon("resources/money.png",      49, 40))
        self.icon_checkouts.setPixmap(   load_icon("resources/briefcase.png",  35, 30))
        self.icon_manage.setPixmap(      load_icon("resources/calendar.png",   50, 45))

    def _build_ui(self):
        self.setObjectName("root")
        self.setStyleSheet("QWidget#root { background-color: #2F2038; border: none; }")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header
        root_layout.addWidget(self._build_header())
        root_layout.addSpacing(20)

        # ── MAIN CONTENT ROW ──────────────────────────────────────────────
        content_row = QWidget()
        content_row.setObjectName("content_row")
        content_row.setStyleSheet(
            "QWidget#content_row { background-color: #2F2038; border: none; }")
        content_row.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        content_layout = QHBoxLayout(content_row)
        content_layout.setContentsMargins(36, 0, 24, 20)
        content_layout.setSpacing(0)

        # Left: stat panel
        stat_panel = self._build_stat_panel()
        stat_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(stat_panel, stretch=5)
        content_layout.addSpacing(18)

        # Vertical separator
        vsep = QFrame()
        vsep.setFrameShape(QFrame.Shape.VLine)
        vsep.setFixedWidth(3)
        vsep.setStyleSheet("background-color: #FFE0E3; border: none;")
        content_layout.addWidget(vsep)
        content_layout.addSpacing(30)

        # Right: manage reservations card
        self.manage_reservations_card = self._build_manage_reservations_card()
        self.manage_reservations_card.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        content_layout.addWidget(self.manage_reservations_card, stretch=4)

        # Content row fills ALL remaining space between header and footer
        root_layout.addWidget(content_row, stretch=1)

        # Footer
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setStyleSheet(
            "QWidget#footer { background-color: #FFE0E3; border: none; }")
        footer.setFixedHeight(37)
        root_layout.addWidget(footer)

    # ── HEADER ──────────────────────────────────────────────────────────────
    def _build_header(self):
        header_outer = QWidget()
        header_outer.setObjectName("header_outer")
        header_outer.setStyleSheet(
            "QWidget#header_outer { background-color: #A797A5; border: none; }")

        header_inner = QWidget()
        header_inner.setObjectName("header_inner")
        header_inner.setStyleSheet(
            "QWidget#header_inner { background-color: #FFE0E3; border: none; }")

        inner_layout = QHBoxLayout(header_inner)
        inner_layout.setContentsMargins(18, 10, 20, 10)
        inner_layout.setSpacing(6)

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(60, 50)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("background: transparent;")
        inner_layout.addWidget(self.logo_label)

        title = QLabel("Staff Dashboard")
        title.setFont(QFont("Segoe UI Semilight", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038; background: transparent;")
        inner_layout.addWidget(title)

        inner_layout.addStretch()

        self.session_label = QLabel("Welcome, Staff")
        self.session_label.setStyleSheet("color: #2F2038; background: transparent;")
        inner_layout.addWidget(self.session_label)

        self.logout_btn = QPushButton("Log out")
        self.logout_btn.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #A02848; }
        """)
        self.logout_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        inner_layout.addWidget(self.logout_btn)

        outer_layout = QVBoxLayout(header_outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(header_inner)

        return header_outer

    # ── STAT PANEL (2x2 grid) ───────────────────────────────────────────────
    def _build_stat_panel(self):
        panel = QWidget()
        panel.setObjectName("stat_panel")
        panel.setStyleSheet(
            "QWidget#stat_panel { background-color: #2F2038; border: 1px solid #412B4E; }")
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.icon_reservations = QLabel()
        self.icon_checkins     = QLabel()
        self.icon_revenue      = QLabel()
        self.icon_checkouts    = QLabel()

        for lbl in [self.icon_reservations, self.icon_checkins,
                    self.icon_revenue, self.icon_checkouts]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: transparent;")

        self.todays_reservation_label = self._make_stat_value("0")
        self.todays_checkins_label    = self._make_stat_value("0")
        self.todays_revenue_label     = self._make_stat_value("₱0")
        self.todays_checkouts_label   = self._make_stat_value("0")

        row1 = QHBoxLayout()
        row1.setSpacing(10)
        row1.addWidget(self._build_stat_card(
            "#9CE5DE", "Today's Reservations",
            self.todays_reservation_label, self.icon_reservations))
        row1.addWidget(self._build_stat_card(
            "#FBCAB9", "Today's Check-ins",
            self.todays_checkins_label, self.icon_checkins))
        layout.addLayout(row1, stretch=1)

        mid_sep = QFrame()
        mid_sep.setFrameShape(QFrame.Shape.HLine)
        mid_sep.setFixedHeight(2)
        mid_sep.setStyleSheet("background-color: #412B4E; border: none;")
        layout.addWidget(mid_sep)

        row2 = QHBoxLayout()
        row2.setSpacing(10)
        row2.addWidget(self._build_stat_card(
            "#F9A79B", "Today's Revenue",
            self.todays_revenue_label, self.icon_revenue))
        row2.addWidget(self._build_stat_card(
            "#B8DFBB", "Today's Check-outs",
            self.todays_checkouts_label, self.icon_checkouts))
        layout.addLayout(row2, stretch=1)

        return panel

    def _build_stat_card(self, color: str, title: str,
                         value_label: QLabel, icon_label: QLabel):
        card = QWidget()
        card.setObjectName("stat_card")
        card.setStyleSheet(
            f"QWidget#stat_card {{ background-color: {color}; border-radius: 6px; border: none; }}")
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(13, 16, 13, 16)
        layout.setSpacing(6)
        layout.addStretch()

        icon_label.setFixedSize(45, 45)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #F2F2F2; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,120); border: none;")

        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_lbl)
        layout.addWidget(sep)
        layout.addWidget(value_label)
        layout.addStretch()

        return card

    def _make_stat_value(self, text: str):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI Semilight", 20, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #F2F2F2; background: transparent;")
        return lbl

    # ── MANAGE RESERVATIONS CARD ────────────────────────────────────────────
    def _build_manage_reservations_card(self):
        outer = QWidget()
        outer.setObjectName("manage_outer")
        outer.setStyleSheet(
            "QWidget#manage_outer { background-color: #2F2038; border: 1px solid #412B4E; }")
        outer.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        outer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        inner = QWidget()
        inner.setObjectName("manage_inner")
        inner.setStyleSheet(
            "QWidget#manage_inner { background-color: #9CAFD6; border-radius: 6px; border: none; }")
        inner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        inner_layout = QVBoxLayout(inner)
        inner_layout.setContentsMargins(18, 18, 18, 18)
        inner_layout.setSpacing(10)
        inner_layout.addStretch()

        top_row = QHBoxLayout()
        top_row.setSpacing(6)

        self.icon_manage = QLabel()
        self.icon_manage.setFixedSize(50, 45)
        self.icon_manage.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_manage.setStyleSheet("background: transparent;")
        top_row.addWidget(self.icon_manage)

        title_col = QVBoxLayout()
        for text in ["Manage", "Reservations"]:
            lbl = QLabel(text)
            lbl.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
            lbl.setStyleSheet("color: #F2F2F2; background: transparent;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_col.addWidget(lbl)
        top_row.addLayout(title_col)
        inner_layout.addLayout(top_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #B6C4E1; border: none;")
        inner_layout.addWidget(sep)

        subtitle = QLabel("Create, View, and Edit Bookings")
        subtitle.setFont(QFont("Segoe UI Semilight", 9, QFont.Weight.Bold))
        subtitle.setStyleSheet("color: #B6C4E1; background: transparent;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner_layout.addWidget(subtitle)
        inner_layout.addStretch()

        outer_layout.addWidget(inner)
        return outer

    # ── PUBLIC SETTERS ───────────────────────────────────────────────────────
    def set_session_label(self, name: str):
        self.session_label.setText(f"Welcome, {name}")

    def set_todays_reservations(self, value):
        self.todays_reservation_label.setText(str(value))

    def set_todays_checkins(self, value):
        self.todays_checkins_label.setText(str(value))

    def set_todays_checkouts(self, value):
        self.todays_checkouts_label.setText(str(value))

    def set_todays_revenue(self, value):
        self.todays_revenue_label.setText(f"₱ {value}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = StaffDashboardView()
    window.show()
    sys.exit(app.exec())