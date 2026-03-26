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


class AdminDashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(900, 600)
        self._build_ui()
        self._load_icons()

    # ── ICON LOADING ────────────────────────────────────────────────────────
    def _load_icons(self):
        # Header logo
        self.logo_label.setPixmap(load_icon("resources/admin_logo.jpg", 60, 50))

        # Stat card icons
        self.icon_reserved.setPixmap(load_icon("resources/reserved.png", 29, 34))
        self.icon_services.setPixmap(load_icon("resources/check.png", 25, 24))
        self.icon_staff.setPixmap(load_icon("resources/briefcase.png", 24, 24))
        self.icon_revenue.setPixmap(load_icon("resources/money.png", 29, 28))

        # Nav card icons
        self.icon_reservation.setPixmap(load_icon("resources/calendar.png", 50, 47))
        self.icon_guest.setPixmap(load_icon("resources/amenities.png", 55, 45))
        self.icon_service.setPixmap(load_icon("resources/services.png", 55, 45))

        # Bottom card icons
        self.icon_account.setPixmap(load_icon("resources/account-management.png", 50, 50))
        self.icon_reports.setPixmap(load_icon("resources/performance-review.png", 55, 45))

    def _build_ui(self):
        self.setStyleSheet("background-color: #2F2038;")

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── HEADER ─────────────────────────────────────────────────────────
        root_layout.addWidget(self._build_header())

        # ── STAT CARDS ROW ─────────────────────────────────────────────────
        stat_wrapper = QWidget()
        stat_wrapper.setObjectName("stat_wrapper")
        stat_wrapper.setStyleSheet(
            "QWidget#stat_wrapper { background-color: #2F2038; border: 1px solid #412B4E; }")
        stat_layout = QHBoxLayout(stat_wrapper)
        stat_layout.setContentsMargins(12, 12, 12, 12)
        stat_layout.setSpacing(10)

        self.total_reservations_label = self._make_stat_value("0")
        self.available_services_label = self._make_stat_value("0")
        self.total_staff_label        = self._make_stat_value("0")
        self.total_revenue_label      = self._make_stat_value("₱0")

        # Icon labels for stat cards (set pixmap in _load_icons)
        self.icon_reserved  = QLabel()
        self.icon_services  = QLabel()
        self.icon_staff     = QLabel()
        self.icon_revenue   = QLabel()

        for lbl in [self.icon_reserved, self.icon_services,
                    self.icon_staff, self.icon_revenue]:
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: transparent;")

        stat_layout.addWidget(self._build_stat_card(
            "#9CE5DE", "Total Reservations",
            self.total_reservations_label, self.icon_reserved))
        stat_layout.addWidget(self._build_stat_card(
            "#B8DFBB", "Available Services",
            self.available_services_label, self.icon_services))
        stat_layout.addWidget(self._build_stat_card(
            "#FBCAB9", "Total Staff",
            self.total_staff_label, self.icon_staff))
        stat_layout.addWidget(self._build_stat_card(
            "#F9A79B", "Total Revenue",
            self.total_revenue_label, self.icon_revenue))

        root_layout.addSpacing(12)
        root_layout.addWidget(stat_wrapper)

        # ── SEPARATOR ──────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(3)
        sep.setStyleSheet("background-color: #FFE0E3; border: none;")
        root_layout.addSpacing(10)
        root_layout.addWidget(sep)
        root_layout.addSpacing(10)

        # ── NAV CARDS ROW (3 cards) ────────────────────────────────────────
        nav_row = QWidget()
        nav_row.setObjectName("nav_row")
        nav_row.setStyleSheet("QWidget#nav_row { background-color: #2F2038; border: none; }")
        nav_layout = QHBoxLayout(nav_row)
        nav_layout.setContentsMargins(73, 0, 73, 0)
        nav_layout.setSpacing(10)

        # Icon labels for nav cards
        self.icon_reservation = QLabel()
        self.icon_guest       = QLabel()
        self.icon_service     = QLabel()

        for lbl in [self.icon_reservation, self.icon_guest, self.icon_service]:
            lbl.setFixedSize(55, 47)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: transparent;")

        self.reservation_card = self._build_nav_card(
            "#9CAFD6", "Reservation", "Management", self.icon_reservation)
        self.guest_card       = self._build_nav_card(
            "#A8B6A1", "Guest", "Management", self.icon_guest)
        self.service_card     = self._build_nav_card(
            "#E96972", "Service", "Management", self.icon_service)

        nav_layout.addWidget(self.reservation_card)
        nav_layout.addWidget(self.guest_card)
        nav_layout.addWidget(self.service_card)

        root_layout.addWidget(nav_row)
        root_layout.addSpacing(12)

        # ── BOTTOM CARDS ROW (2 cards) ─────────────────────────────────────
        bottom_wrapper = QWidget()
        bottom_wrapper.setObjectName("bottom_wrapper")
        bottom_wrapper.setStyleSheet(
            "QWidget#bottom_wrapper { background-color: #2F2038; border: 1px solid #412B4E; }")
        bottom_layout = QHBoxLayout(bottom_wrapper)
        bottom_layout.setContentsMargins(12, 12, 12, 12)
        bottom_layout.setSpacing(10)

        # Icon labels for bottom cards
        self.icon_account = QLabel()
        self.icon_reports = QLabel()

        for lbl in [self.icon_account, self.icon_reports]:
            lbl.setFixedSize(50, 50)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet("background: transparent;")

        self.account_card = self._build_bottom_card(
            "#B278C5", "Account Management",
            "View Sales & Revenue Reports", "#C194D0", self.icon_account)
        self.reports_card = self._build_bottom_card(
            "#7F8C99", "Reports and Analytics",
            "Configure System Preferences", "#8D99A4", self.icon_reports)

        bottom_layout.addWidget(self.account_card)
        bottom_layout.addWidget(self.reports_card)

        root_layout.addWidget(bottom_wrapper)
        root_layout.addSpacing(18)

        # ── FOOTER STRIP ───────────────────────────────────────────────────
        footer = QWidget()
        footer.setObjectName("footer")
        footer.setStyleSheet("QWidget#footer { background-color: #FFE0E3; border: none; }")
        footer.setFixedHeight(30)
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

        # Logo
        self.logo_label = QLabel()
        self.logo_label.setFixedSize(60, 50)
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setStyleSheet("background: transparent;")
        inner_layout.addWidget(self.logo_label)

        # Title
        title = QLabel("Admin Dashboard")
        title.setFont(QFont("Segoe UI Semilight", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038; background: transparent;")
        inner_layout.addWidget(title)

        inner_layout.addStretch()

        # Welcome label
        self.session_label = QLabel("Welcome, Admin")
        self.session_label.setStyleSheet(
            "color: #2F2038; background: transparent;")
        inner_layout.addWidget(self.session_label)

        # Logout button
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

    # ── STAT CARD ───────────────────────────────────────────────────────────
    def _build_stat_card(self, color: str, title: str,
                         value_label: QLabel, icon_label: QLabel):
        card = QWidget()
        card.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        card.setFixedHeight(90)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(13, 13, 13, 8)
        layout.setSpacing(8)

        # Left: icon
        icon_label.setFixedSize(30, 34)
        layout.addWidget(icon_label)

        # Right: title + separator + value
        right = QVBoxLayout()
        right.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI Semilight", 9, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #F2F2F2; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: rgba(255,255,255,120); border: none;")

        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        right.addWidget(title_lbl)
        right.addWidget(sep)
        right.addWidget(value_label)

        layout.addLayout(right)

        return card

    def _make_stat_value(self, text: str):
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI Semilight", 22, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #F2F2F2; background: transparent;")
        return lbl

    # ── NAV CARD (3-card row) ────────────────────────────────────────────────
    def _build_nav_card(self, color: str, line1: str,
                        line2: str, icon_label: QLabel):
        card = QWidget()
        card.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        card.setFixedHeight(110)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(card)
        layout.setContentsMargins(13, 28, 13, 28)
        layout.setSpacing(6)

        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        l1 = QLabel(line1)
        l1.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        l1.setStyleSheet("color: #F2F2F2; background: transparent;")

        l2 = QLabel(line2)
        l2.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        l2.setStyleSheet("color: #F2F2F2; background: transparent;")

        text_layout.addWidget(l1)
        text_layout.addWidget(l2)
        layout.addLayout(text_layout)
        layout.addStretch()

        return card

    # ── BOTTOM CARD (2-card row) ─────────────────────────────────────────────
    def _build_bottom_card(self, color: str, title: str,
                           subtitle: str, sub_color: str,
                           icon_label: QLabel):
        card = QWidget()
        card.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
        card.setFixedHeight(100)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        card.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        layout = QHBoxLayout(card)
        layout.setContentsMargins(20, 22, 20, 22)
        layout.setSpacing(18)

        layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #F2F2F2; background: transparent;")

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {sub_color}; border: none;")

        sub_lbl = QLabel(subtitle)
        sub_lbl.setFont(QFont("Segoe UI Semilight", 9, QFont.Weight.Bold))
        sub_lbl.setStyleSheet(f"color: {sub_color}; background: transparent;")

        text_layout.addWidget(title_lbl)
        text_layout.addWidget(sep)
        text_layout.addWidget(sub_lbl)

        layout.addLayout(text_layout)
        layout.addStretch()

        return card

    # ── PUBLIC SETTERS (called by controller) ────────────────────────────────
    def set_session_label(self, name: str):
        self.session_label.setText(f"Welcome, {name}")

    def set_available_services(self, value):
        self.available_services_label.setText(str(value))

    def set_total_staff(self, value):
        self.total_staff_label.setText(str(value))

    def set_total_revenue(self, value):
        self.total_revenue_label.setText(f"₱ {value}")

    def set_total_reservations(self, value):
        self.total_reservations_label.setText(str(value))


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = AdminDashboardView()
    window.show()
    sys.exit(app.exec())