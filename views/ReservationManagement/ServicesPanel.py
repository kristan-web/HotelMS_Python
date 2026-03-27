import sys
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QComboBox, QLineEdit, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor


class ServicesPanel(QWidget):
    
    # Signal definitions for controller communication
    book_service_requested = pyqtSignal(dict)  # service booking data
    delete_booking_requested = pyqtSignal(str)  # booking_id
    refresh_requested = pyqtSignal()
    calculate_total_requested = pyqtSignal(str)  # service_id
    
    def __init__(self):
        super().__init__()
        print("🟢 ServicesPanel.__init__ called")
        
        # Match the expanding policy
        self.setSizePolicy(self.sizePolicy().Policy.Expanding, self.sizePolicy().Policy.Expanding)
        
        # Color Palette
        self.BG_ROOT = "#2F2038"      
        self.BG_CARD = "#3D2850"      
        self.BORDER_COLOR = "#412B4E" 
        self.TEXT_LAVENDER = "#FFE0E3" 
        self.ACCENT_CRIMSON = "#BE3455" 
        self.INPUT_BG = "#F9F5FF"     

        # Data storage (will be populated by controller)
        self.static_bookings = []
        self.all_guests = []
        self.all_services = []
        self.current_service_price = 0

        self.init_ui()
        self._connect_signals()

    def init_ui(self):
        self.setObjectName("service_root")
        self.setStyleSheet(f"QWidget#service_root {{ background-color: {self.BG_ROOT}; border: none; }}")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # ── TOP FORM PANEL (Triple Card Layout) ───────────────────────────
        main_layout.addWidget(self._build_booking_panel())

        # ── BOTTOM TABLE PANEL (Management Section) ───────────────────────
        main_layout.addWidget(self._build_table_panel(), stretch=1)

    def _connect_signals(self):
        """Connect internal signals"""
        self.btn_book.clicked.connect(self.handle_book)
        self.btn_delete.clicked.connect(self.handle_delete)
        self.btn_refresh.clicked.connect(self.handle_refresh)
        self.combo_service.currentTextChanged.connect(self.handle_service_selected)
        self.txt_duration.textChanged.connect(self.handle_duration_changed)

    def _build_booking_panel(self):
        form_outer = QFrame()
        form_outer.setObjectName("form_outer")
        form_outer.setStyleSheet(f"""
            QFrame#form_outer {{
                background-color: {self.BG_ROOT};
                border: 1px solid {self.BORDER_COLOR};
                border-radius: 6px;
            }}
        """)

        layout = QHBoxLayout(form_outer)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Sub-panel 1: Selection
        p1 = self._create_sub_panel()
        lay1 = QVBoxLayout(p1)
        lay1.addWidget(self._styled_label("Guest Name:*"))
        self.combo_guest = self._styled_combo([])
        lay1.addWidget(self.combo_guest)
        lay1.addWidget(self._styled_label("Service Type:*"))
        self.combo_service = self._styled_combo([])
        lay1.addWidget(self.combo_service)
        layout.addWidget(p1, stretch=1)

        # Sub-panel 2: Duration & Scheduled Time
        p2 = self._create_sub_panel()
        lay2 = QVBoxLayout(p2)
        lay2.addWidget(self._styled_label("Duration (mins):*"))
        self.txt_duration = self._styled_input("60")
        lay2.addWidget(self.txt_duration)
        lay2.addWidget(self._styled_label("Scheduled Time:"))
        self.scheduled_time = self._styled_input(datetime.now().strftime("%Y-%m-%d %H:%M"))
        lay2.addWidget(self.scheduled_time)
        lay2.addStretch()
        layout.addWidget(p2, stretch=1)

        # Sub-panel 3: Confirmation
        p3 = self._create_sub_panel()
        lay3 = QVBoxLayout(p3)
        self.lbl_total = QLabel("Total: ₱0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setStyleSheet(f"color: {self.TEXT_LAVENDER}; font-size: 16pt; font-weight: bold; margin-bottom: 5px;")
        
        self.btn_book = self._action_button("BOOK NOW", self.ACCENT_CRIMSON)
        self.btn_book.setFixedWidth(200)
        
        lay3.addWidget(self.lbl_total)
        lay3.addWidget(self.btn_book, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(p3, stretch=1)

        return form_outer

    def _build_table_panel(self):
        table_outer = QFrame()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet(f"QFrame#table_outer {{ background-color: {self.BG_ROOT}; border: 1px solid {self.BORDER_COLOR}; border-radius: 6px; }}")
        
        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)

        # Table Toolbar
        tools = QHBoxLayout()
        self.btn_refresh = self._action_button("REFRESH", "#412B4E")
        self.btn_delete = self._action_button("DELETE", self.ACCENT_CRIMSON)
        
        tools.addWidget(self.btn_refresh)
        tools.addWidget(self.btn_delete)
        tools.addStretch()
        layout.addLayout(tools)

        # Table Setup
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Guest", "Service", "Scheduled", "Duration", "Total", "Status"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setStyleSheet("background-color: #412B4E !important;")
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {self.BG_CARD}; color: #F2F2F2;
                gridline-color: {self.BORDER_COLOR}; border-radius: 4px; border: none;
            }}
            QHeaderView::section {{
                background-color: {self.BORDER_COLOR}; color: {self.TEXT_LAVENDER};
                font-weight: bold; border: none; padding: 6px;
                border-right: 1px solid #2F2038;
                border-bottom: 1px solid #2F2038;
            }}
            QTableCornerButton::section {{
                background-color: {self.BORDER_COLOR};
                border: none;
                border-right: 1px solid #2F2038;
                border-bottom: 1px solid #2F2038;
            }}
            QTableWidget::item:selected {{ background-color: {self.ACCENT_CRIMSON}; color: {self.TEXT_LAVENDER}; }}
            QTableWidget::item:hover {{ background-color: #5A3D6B; }}
        """)
        
        layout.addWidget(self.table)
        return table_outer

    # --- UI Helpers ---
    def _create_sub_panel(self):
        p = QFrame()
        p.setStyleSheet(f"background-color: {self.BG_CARD}; border-radius: 6px;")
        return p

    def _styled_label(self, t):
        l = QLabel(t)
        l.setStyleSheet(f"color: {self.TEXT_LAVENDER}; background: transparent; font-size: 11pt;")
        l.setFont(QFont("Segoe UI Semilight", 11))
        return l

    def _styled_input(self, text=""):
        e = QLineEdit(text)
        e.setFixedHeight(35)
        e.setStyleSheet(f"background-color: {self.INPUT_BG}; color: #2F2038; border-radius: 4px; padding-left: 10px;")
        return e

    def _styled_combo(self, items):
        c = QComboBox()
        if items:
            c.addItems(items)
        c.setFixedHeight(35)
        c.setStyleSheet(f"""
            QComboBox {{
                background-color: {self.INPUT_BG};
                color: #2F2038;
                border-radius: 4px;
                padding-left: 5px;
            }}
            QComboBox:focus {{
                border: 1px solid {self.ACCENT_CRIMSON};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background-color: {self.BG_CARD};
                color: {self.TEXT_LAVENDER};
                selection-background-color: {self.ACCENT_CRIMSON};
            }}
        """)
        return c

    def _action_button(self, t, color):
        b = QPushButton(t)
        b.setFixedSize(110, 34)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        b.setStyleSheet(f"""
            QPushButton {{
                background-color: {color}; color: #FFE0E3;
                border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        return b

    def _get_service_by_id(self, service_id):
        """Get service details by ID"""
        for s in self.all_services:
            if s.get('id') == service_id or s.get('service_id') == service_id:
                return s
        return None

    # --- Event Handlers (Emit Signals) ---
    def handle_book(self):
        """Emit book_service signal with form data"""
        print("🔵 ServicesPanel.handle_book called")
        
        # Validate required fields
        guest_id = self.combo_guest.currentData()
        if not guest_id:
            self.show_error("Please select a guest.")
            return
        
        service_id = self.combo_service.currentData()
        if not service_id:
            self.show_error("Please select a service.")
            return
        
        if not self.txt_duration.text():
            self.show_error("Please enter duration.")
            return
        
        try:
            duration = int(self.txt_duration.text())
            if duration <= 0:
                self.show_error("Duration must be greater than 0.")
                return
        except ValueError:
            self.show_error("Duration must be a valid number.")
            return
        
        # Calculate total properly
        service = self._get_service_by_id(service_id)
        if not service:
            self.show_error("Service not found.")
            return
        
        unit_price = float(service['price'])
        total = unit_price
        
        booking_data = {
            'guest_id': guest_id,
            'service_id': service_id,
            'duration': duration,
            'scheduled_time': self.scheduled_time.text(),
            'total': total,
            'unit_price': unit_price
        }
        
        print(f"📝 Emitting book_service_requested with: {booking_data}")
        self.book_service_requested.emit(booking_data)

    def handle_delete(self):
        """Emit delete_booking signal for selected row"""
        selected = self.table.selectedItems()
        if selected:
            row = selected[0].row()
            booking_id = self.get_table_value(row, 0)
            if self.confirm_delete():
                self.delete_booking_requested.emit(booking_id)
        else:
            self.show_error("Please select a booking to delete.")

    def handle_refresh(self):
        """Emit refresh signal"""
        self.refresh_requested.emit()

    def handle_service_selected(self, service_name):
        """Emit signal to calculate total when service changes"""
        service_id = self.combo_service.currentData()
        if service_id:
            duration_text = self.txt_duration.text()
            if duration_text and duration_text.isdigit() and int(duration_text) > 0:
                self.calculate_total_requested.emit(str(service_id))
            else:
                service = self._get_service_by_id(service_id)
                if service:
                    self.lbl_total.setText(f"Total: ₱{float(service['price']):,.2f}")

    def handle_duration_changed(self, duration):
        """Emit signal to calculate total when duration changes"""
        service_id = self.combo_service.currentData()
        if service_id and duration and duration.isdigit() and int(duration) > 0:
            self.calculate_total_requested.emit(str(service_id))

    # --- Public Methods ---
    def load_guests(self, guests: list):
        """
        Load guests into combo box
        guests: list of dicts with keys: id, first_name, last_name
        """
        print(f"🟢 ServicesPanel.load_guests called with {len(guests)} guests")
        self.all_guests = guests
        self.combo_guest.clear()
        
        current_data = self.combo_guest.currentData()
        selected_index = -1
        
        for idx, g in enumerate(guests):
            guest_id = g.get('id') or g.get('guest_id')
            first_name = g.get('first_name', '')
            last_name = g.get('last_name', '')
            display_name = f"{first_name} {last_name}".strip()
            
            if not display_name:
                display_name = "Unknown Guest"
            
            self.combo_guest.addItem(display_name, guest_id)
            
            if current_data and guest_id == current_data:
                selected_index = idx
        
        if selected_index >= 0:
            self.combo_guest.setCurrentIndex(selected_index)
        
        print(f"📊 Loaded {len(guests)} guests into ServicesPanel combo")
        
        if len(guests) == 0:
            self.combo_guest.addItem("No guests available", None)
            self.combo_guest.setEnabled(False)
        else:
            self.combo_guest.setEnabled(True)

    def load_services(self, services: list):
        """
        Load services into combo box
        services: list of dicts with keys: id, name, price
        """
        print(f"🟢 ServicesPanel.load_services called with {len(services)} services")
        self.all_services = services
        self.combo_service.clear()
        
        for s in services:
            service_id = s.get('id') or s.get('service_id')
            self.combo_service.addItem(s.get('name', ''), service_id)
            if s.get('price'):
                self.current_service_price = float(s['price'])
        
        print(f"📊 Loaded {len(services)} services into ServicesPanel combo")
        
        if len(services) == 0:
            self.combo_service.addItem("No services available", None)
            self.combo_service.setEnabled(False)
        else:
            self.combo_service.setEnabled(True)

    def load_bookings(self, bookings: list):
        """Load bookings into table"""
        print(f"🟢 ServicesPanel.load_bookings called with {len(bookings)} bookings")
        self.static_bookings = bookings
        self.table.setRowCount(0)
        for b in bookings:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)
            for col, key in enumerate(["booking_id", "guest_name", "service_name", "scheduled_time", "duration", "total", "status"]):
                value = b.get(key, "")
                if key == "total" and value:
                    try:
                        value = f"₱{float(value):,.2f}"
                    except (ValueError, TypeError):
                        pass
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.table.setItem(row, col, item)
        
        print(f"📊 Loaded {len(bookings)} bookings into ServicesPanel table")

    def load_data(self):
        """Legacy method for backward compatibility"""
        self.load_bookings(self.static_bookings)

    def load_sample_data(self):
        """Load sample data for testing"""
        sample_bookings = [
            {"booking_id": "1", "guest_name": "John Doe", "service_name": "Spa Massage", 
             "scheduled_time": "2024-05-20 14:00", "duration": "60 mins", "total": "1500.00", "status": "COMPLETED"},
            {"booking_id": "2", "guest_name": "Jane Smith", "service_name": "Gym Session", 
             "scheduled_time": "2024-05-21 09:00", "duration": "120 mins", "total": "500.00", "status": "PENDING"},
        ]
        self.load_bookings(sample_bookings)
        
        sample_guests = [
            {"id": "1", "first_name": "John", "last_name": "Doe"},
            {"id": "2", "first_name": "Jane", "last_name": "Smith"},
        ]
        self.load_guests(sample_guests)
        
        sample_services = [
            {"id": "1", "name": "Spa Massage", "price": "1500"},
            {"id": "2", "name": "Gym Session", "price": "500"},
            {"id": "3", "name": "Laundry", "price": "300"},
        ]
        self.load_services(sample_services)

    def set_total(self, total: str):
        """Set the total label with formatted price"""
        try:
            total_float = float(total)
            self.lbl_total.setText(f"Total: ₱{total_float:,.2f}")
        except (ValueError, TypeError):
            self.lbl_total.setText(f"Total: ₱{total}")

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""

    def confirm_delete(self) -> bool:
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to cancel this service booking?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ServicesPanel()
    window.resize(1100, 750)
    window.load_sample_data()
    window.show()
    sys.exit(app.exec())