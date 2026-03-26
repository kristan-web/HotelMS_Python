import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QHBoxLayout, QFrame, QHeaderView, QAbstractItemView,
    QSizePolicy, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor, QPixmap


def load_icon(path: str, w: int, h: int) -> QPixmap:
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    px = QPixmap(os.path.join(base, path))
    if px.isNull():
        return QPixmap()
    return px.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio,
                     Qt.TransformationMode.SmoothTransformation)


class ReceiptView(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Receipt")
        self.setMinimumSize(800, 750)
        self._build_ui()
        self._load_icons()

    def _load_icons(self):
        self.logo_lbl.setPixmap(load_icon("resources/admin_logo.jpg", 200, 200))

    def _build_ui(self):
        self.setObjectName("receipt_root")
        self.setStyleSheet("""
            QWidget#receipt_root {
                background-color: #2F2038;
                border: none;
            }
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(30, 30, 30, 30)
        root.setSpacing(15)

        # ── HEADER SECTION ──────────────────────────────────────────────────
        header_layout = QHBoxLayout()
        header_layout.setSpacing(20)

        # Left side - Hotel Info
        hotel_info = QVBoxLayout()
        hotel_info.setSpacing(4)

        hotel_name = QLabel("Kobu Hotel and Reservations")
        hotel_name.setFont(QFont("Segoe UI Semilight", 14, QFont.Weight.Bold))
        hotel_name.setStyleSheet("color: #FFE0E3; background: transparent;")
        hotel_info.addWidget(hotel_name)

        address1 = QLabel("1234 Kobu St.")
        address1.setFont(QFont("Segoe UI Semilight", 10))
        address1.setStyleSheet("color: #A797A5; background: transparent;")
        hotel_info.addWidget(address1)

        address2 = QLabel("Dasmariñas Cavite, ST 1234")
        address2.setFont(QFont("Segoe UI Semilight", 10))
        address2.setStyleSheet("color: #A797A5; background: transparent;")
        hotel_info.addWidget(address2)

        header_layout.addLayout(hotel_info)
        header_layout.addStretch()

        # Right side - Logo
        self.logo_lbl = QLabel()
        self.logo_lbl.setFixedSize(80, 80)
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setStyleSheet("background: transparent;")
        header_layout.addWidget(self.logo_lbl)

        root.addLayout(header_layout)

        # ── RECEIPT TITLE ───────────────────────────────────────────────────
        receipt_title = QLabel("R E C E I P T")
        receipt_title.setFont(QFont("Segoe UI Semibold", 24, QFont.Weight.Bold))
        receipt_title.setStyleSheet("color: #BE3455; background: transparent;")
        receipt_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        root.addWidget(receipt_title)

        # ── SEPARATOR ──────────────────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(2)
        sep.setStyleSheet("background-color: #412B4E; border: none;")
        root.addWidget(sep)

        # ── BILLED TO SECTION ──────────────────────────────────────────────
        billed_to = QLabel("Billed To")
        billed_to.setFont(QFont("Segoe UI Semibold", 10, QFont.Weight.Bold))
        billed_to.setStyleSheet("color: #FFE0E3; background: transparent;")
        root.addWidget(billed_to)

        customer_name = QLabel("Customer Name")
        customer_name.setFont(QFont("Segoe UI Semilight", 14))
        customer_name.setStyleSheet("color: #FFE0E3; background: transparent;")
        root.addWidget(customer_name)

        # ── CUSTOMER INFO ROW ──────────────────────────────────────────────
        info_row = QHBoxLayout()
        info_row.setSpacing(20)

        # Left side - Customer address
        customer_address = QVBoxLayout()
        address_line1 = QLabel("1234 Kobu St.")
        address_line1.setFont(QFont("Segoe UI Semilight", 10))
        address_line1.setStyleSheet("color: #A797A5; background: transparent;")
        customer_address.addWidget(address_line1)

        address_line2 = QLabel("Dasmariñas Cavite, ST 1234")
        address_line2.setFont(QFont("Segoe UI Semilight", 10))
        address_line2.setStyleSheet("color: #A797A5; background: transparent;")
        customer_address.addWidget(address_line2)

        info_row.addLayout(customer_address)
        info_row.addStretch()

        # Right side - Receipt info
        receipt_info = QVBoxLayout()
        receipt_info.setAlignment(Qt.AlignmentFlag.AlignRight)

        receipt_num_row = QHBoxLayout()
        receipt_num_lbl = QLabel("Receipt #:")
        receipt_num_lbl.setFont(QFont("Segoe UI Semibold", 10, QFont.Weight.Bold))
        receipt_num_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        self.receipt_num = QLabel("0000456")
        self.receipt_num.setFont(QFont("Segoe UI Semilight", 10))
        self.receipt_num.setStyleSheet("color: #FFE0E3; background: transparent;")
        receipt_num_row.addWidget(receipt_num_lbl)
        receipt_num_row.addWidget(self.receipt_num)
        receipt_info.addLayout(receipt_num_row)

        date_row = QHBoxLayout()
        date_lbl = QLabel("Receipt Date:")
        date_lbl.setFont(QFont("Segoe UI Semibold", 10, QFont.Weight.Bold))
        date_lbl.setStyleSheet("color: #FFE0E3; background: transparent;")
        self.receipt_date = QLabel("11-04-23")
        self.receipt_date.setFont(QFont("Segoe UI Semilight", 10))
        self.receipt_date.setStyleSheet("color: #FFE0E3; background: transparent;")
        date_row.addWidget(date_lbl)
        date_row.addWidget(self.receipt_date)

        receipt_info.addLayout(date_row)
        info_row.addLayout(receipt_info)

        root.addLayout(info_row)

        root.addSpacing(10)

        # ── TABLE (ITEMS) ───────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "reservation_id", "Service", "Quantity", "Unit Price", "Discount", "Tax", "Total"
        ])
        self.table.setFont(QFont("Segoe UI Semilight", 10))
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850;
                color: #F2F2F2;
                border: 2px solid #412B4E;
                border-radius: 6px;
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
        
        root.addWidget(self.table)

        # ── TOTALS SECTION ─────────────────────────────────────────────────
        totals_widget = QWidget()
        totals_widget.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        totals_layout = QVBoxLayout(totals_widget)
        totals_layout.setContentsMargins(20, 15, 20, 15)
        totals_layout.setSpacing(8)

        # Subtotal
        subtotal_row = QHBoxLayout()
        subtotal_lbl = QLabel("Subtotal")
        subtotal_lbl.setFont(QFont("Segoe UI Semilight", 10))
        subtotal_lbl.setStyleSheet("color: #FFE0E3;")
        self.subtotal_val = QLabel("₱350.00")
        self.subtotal_val.setFont(QFont("Segoe UI Semilight", 10))
        self.subtotal_val.setStyleSheet("color: #FFE0E3;")
        subtotal_row.addWidget(subtotal_lbl)
        subtotal_row.addStretch()
        subtotal_row.addWidget(self.subtotal_val)
        totals_layout.addLayout(subtotal_row)

        # Tax
        tax_row = QHBoxLayout()
        tax_lbl = QLabel("Sales Tax (5%)")
        tax_lbl.setFont(QFont("Segoe UI Semilight", 10))
        tax_lbl.setStyleSheet("color: #FFE0E3;")
        self.tax_val = QLabel("₱30.00")
        self.tax_val.setFont(QFont("Segoe UI Semilight", 10))
        self.tax_val.setStyleSheet("color: #FFE0E3;")
        tax_row.addWidget(tax_lbl)
        tax_row.addStretch()
        tax_row.addWidget(self.tax_val)
        totals_layout.addLayout(tax_row)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setFixedHeight(1)
        sep2.setStyleSheet("background-color: #412B4E;")
        totals_layout.addWidget(sep2)

        # Total
        total_row = QHBoxLayout()
        total_lbl = QLabel("Total (PHP)")
        total_lbl.setFont(QFont("Segoe UI Semibold", 10, QFont.Weight.Bold))
        total_lbl.setStyleSheet("color: #FFE0E3;")
        self.total_val = QLabel("₱380.00")
        self.total_val.setFont(QFont("Segoe UI Semibold", 10, QFont.Weight.Bold))
        self.total_val.setStyleSheet("color: #BE3455;")
        total_row.addWidget(total_lbl)
        total_row.addStretch()
        total_row.addWidget(self.total_val)
        totals_layout.addLayout(total_row)

        root.addWidget(totals_widget)

        # ── FOOTER NOTES ───────────────────────────────────────────────────
        footer_layout = QVBoxLayout()
        footer_layout.setSpacing(5)

        note_lbl = QLabel("Notes:")
        note_lbl.setFont(QFont("Segoe UI Semibold", 10, QFont.Weight.Bold))
        note_lbl.setStyleSheet("color: #FFE0E3;")
        footer_layout.addWidget(note_lbl)

        thank_you = QLabel("Thank you for your purchase! All sales are final after 30 days.")
        thank_you.setFont(QFont("Segoe UI Semilight", 9))
        thank_you.setStyleSheet("color: #A797A5;")
        footer_layout.addWidget(thank_you)

        warranty = QLabel("Please retain this receipt for warranty or exchange purposes.")
        warranty.setFont(QFont("Segoe UI Semilight", 9))
        warranty.setStyleSheet("color: #A797A5;")
        footer_layout.addWidget(warranty)

        support = QLabel("For questions or support, contact us at kobu@hotel.com")
        support.setFont(QFont("Segoe UI Semilight", 9))
        support.setStyleSheet("color: #A797A5;")
        footer_layout.addWidget(support)

        root.addLayout(footer_layout)

        # ── BACK BUTTON ────────────────────────────────────────────────────
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFont(QFont("Segoe UI Semilight", 11, QFont.Weight.Bold))
        self.back_btn.setFixedHeight(40)
        self.back_btn.setFixedWidth(100)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #412B4E;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 16px;
            }
            QPushButton:hover {
                background-color: #5A3D6B;
            }
        """)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.clicked.connect(self.go_back)
        
        back_row = QHBoxLayout()
        back_row.addWidget(self.back_btn)
        back_row.addStretch()
        root.addLayout(back_row)

    def go_back(self):
        """Navigate back"""
        if self.main_window:
            self.main_window.show()
        self.close()

    def load_receipt_data(self, data: dict):
        """Load receipt data into view"""
        if 'receipt_num' in data:
            self.receipt_num.setText(data['receipt_num'])
        if 'receipt_date' in data:
            self.receipt_date.setText(data['receipt_date'])
        if 'customer_name' in data:
            # Update customer name label
            pass
        if 'subtotal' in data:
            self.subtotal_val.setText(f"₱{data['subtotal']:.2f}")
        if 'tax' in data:
            self.tax_val.setText(f"₱{data['tax']:.2f}")
        if 'total' in data:
            self.total_val.setText(f"₱{data['total']:.2f}")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    w = ReceiptView()
    
    # Sample data
    sample_data = {
        'receipt_num': '0000456',
        'receipt_date': '2024-01-15',
        'customer_name': 'John Doe',
        'subtotal': 350.00,
        'tax': 30.00,
        'total': 380.00
    }
    
    w.load_receipt_data(sample_data)
    w.show()
    sys.exit(app.exec())