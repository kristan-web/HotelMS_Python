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
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor

# ── FIXED IMPORT ──────────────────────────────────────────────────────────
from views.ReservationManagement.DatePicker import DatePickerDialog 


class ReservationPanel(QWidget):
    FMT = "%b %d, %Y"
    
    # Signal definitions for controller communication
    find_rooms_requested = pyqtSignal(str, str)  # check_in_date, check_out_date
    confirm_reservation_requested = pyqtSignal(dict)  # reservation data
    check_in_requested = pyqtSignal(str)  # reservation_id
    check_out_requested = pyqtSignal(str)  # reservation_id
    cancel_reservation_requested = pyqtSignal(str)  # reservation_id - ADDED
    delete_reservation_requested = pyqtSignal(str)  # reservation_id
    refresh_requested = pyqtSignal()
    filter_requested = pyqtSignal(str)  # status filter
    room_selected_requested = pyqtSignal(str)  # room_id - for total calculation
    dates_changed = pyqtSignal()  # when dates change

    def __init__(self):
        super().__init__()
        self.check_in_date = None
        self.check_out_date = None
        self._build_ui()
        self._connect_signals()

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

    def _connect_signals(self):
        """Connect internal signals"""
        self.btn_find_rooms.clicked.connect(self.handle_find_rooms)
        self.btn_confirm.clicked.connect(self.handle_confirm_reservation)
        self.btn_check_in.clicked.connect(self.handle_check_in)
        self.btn_check_out.clicked.connect(self.handle_check_out)
        self.btn_cancel.clicked.connect(self.handle_cancel_reservation)  # ADDED
        self.btn_delete.clicked.connect(self.handle_delete_reservation)
        self.btn_refresh.clicked.connect(self.handle_refresh)
        self.status_filter.currentTextChanged.connect(self.handle_filter)
        self.room_combo.currentIndexChanged.connect(self.handle_room_selected)
        self.dates_changed.connect(self.handle_dates_changed)

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

        layout.addWidget(self._styled_label("Guest Name:*", lbl_style))
        self.guest_combo = QComboBox()
        self.guest_combo.setStyleSheet(combo_style)
        self.guest_combo.setFixedHeight(35)
        layout.addWidget(self.guest_combo)

        layout.addWidget(self._styled_label("Select Room:*", lbl_style))
        self.room_combo = QComboBox()
        self.room_combo.setStyleSheet(combo_style)
        self.room_combo.setFixedHeight(35)
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
        layout.addWidget(self._styled_label("Check-In Date:*", lbl_style))
        h1 = QHBoxLayout()
        self.check_in_field = QLineEdit()
        self.check_in_field.setReadOnly(True)
        self.check_in_field.setStyleSheet(field_style)
        self.check_in_field.setFixedHeight(35)
        btn_in = QPushButton("📅")
        btn_in.setFixedSize(35, 35)
        btn_in.setStyleSheet(btn_pick_style)
        btn_in.clicked.connect(self.handle_pick_check_in)
        h1.addWidget(self.check_in_field)
        h1.addWidget(btn_in)
        layout.addLayout(h1)

        # Check Out
        layout.addWidget(self._styled_label("Check-Out Date:*", lbl_style))
        h2 = QHBoxLayout()
        self.check_out_field = QLineEdit()
        self.check_out_field.setReadOnly(True)
        self.check_out_field.setStyleSheet(field_style)
        self.check_out_field.setFixedHeight(35)
        btn_out = QPushButton("📅")
        btn_out.setFixedSize(35, 35)
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
        self.btn_find_rooms.setFixedHeight(40)
        self.btn_find_rooms.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_find_rooms.setStyleSheet("""
            QPushButton { background-color: #412B4E; color: #FFE0E3; border-radius: 6px; font-weight: bold; font-size: 11pt; }
            QPushButton:hover { background-color: #5A3D6B; }
        """)

        self.btn_confirm = QPushButton("Confirm Reservation")
        self.btn_confirm.setFixedHeight(40)
        self.btn_confirm.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_confirm.setStyleSheet("""
            QPushButton { background-color: #FFE0E3; color: #2F2038; border-radius: 6px; font-weight: bold; font-size: 11pt; }
            QPushButton:hover { background-color: #F0C8CC; }
        """)

        self.lbl_total = QLabel("Total: ₱0.00")
        self.lbl_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_total.setStyleSheet("color: #FFE0E3; font-size: 18pt; font-weight: bold; margin-top: 10px;")

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
        self.status_filter.setFixedHeight(35)
        self.status_filter.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px; padding-left: 8px;")

        btn_row.addWidget(self._styled_label("Filter Status:", "color: #FFE0E3; font-size: 11pt;"))
        btn_row.addWidget(self.status_filter)
        btn_row.addSpacing(20)

        # Action Buttons (Check In, Check Out, Cancel, Refresh)
        self.btn_check_in = self._action_button("Check In", "#412B4E")
        self.btn_check_out = self._action_button("Check Out", "#412B4E")
        self.btn_cancel = self._action_button("Cancel", "#BE3455")  # ADDED
        self.btn_delete = self._action_button("Delete", "#7B1C2E")
        self.btn_refresh = self._action_button("Refresh", "#412B4E")

        btn_row.addWidget(self.btn_check_in)
        btn_row.addWidget(self.btn_check_out)
        btn_row.addWidget(self.btn_cancel)  # ADDED
        btn_row.addWidget(self.btn_delete)
        btn_row.addWidget(self.btn_refresh)
        btn_row.addStretch()
        
        layout.addLayout(btn_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Guest", "Room", "Check-In", "Check-Out", "Nights", "Total", "Status"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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

    # ── Event Handlers (Emit Signals) ───────────────────────────────────────
    def handle_pick_check_in(self):
        d = DatePickerDialog.show_dialog(self, "Check-In Date", date.today())
        if d:
            self.check_in_date = d
            self.check_in_field.setText(d.strftime(self.FMT))
            self.dates_changed.emit()

    def handle_pick_check_out(self):
        d = DatePickerDialog.show_dialog(self, "Check-Out Date", date.today())
        if d:
            self.check_out_date = d
            self.check_out_field.setText(d.strftime(self.FMT))
            self.dates_changed.emit()

    def handle_find_rooms(self):
        if self.check_in_date and self.check_out_date:
            if self.check_in_date >= self.check_out_date:
                self.show_error("Check-out date must be after check-in date.")
                return
            self.find_rooms_requested.emit(
                self.check_in_date.strftime("%Y-%m-%d"),
                self.check_out_date.strftime("%Y-%m-%d")
            )
        else:
            self.show_error("Please select both check-in and check-out dates.")

    def handle_room_selected(self, index):
        """Handle room selection from combo box"""
        if index >= 0:
            room_id = self.room_combo.currentData()
            if room_id:
                self.room_selected_requested.emit(str(room_id))

    def handle_dates_changed(self):
        """Handle date changes to update total"""
        if self.check_in_date and self.check_out_date and self.room_combo.currentData():
            self.room_selected_requested.emit(str(self.room_combo.currentData()))

    def handle_confirm_reservation(self):
        # Validate required fields
        if not self.guest_combo.currentData():
            self.show_error("Please select a guest.")
            return
        
        if not self.room_combo.currentData():
            self.show_error("Please select a room.")
            return
        
        if not self.check_in_date or not self.check_out_date:
            self.show_error("Please select check-in and check-out dates.")
            return
        
        if self.check_in_date >= self.check_out_date:
            self.show_error("Check-out date must be after check-in date.")
            return
        
        reservation_data = {
            'guest_id': self.guest_combo.currentData(),
            'room_id': self.room_combo.currentData(),
            'check_in': self.check_in_date.strftime("%Y-%m-%d"),
            'check_out': self.check_out_date.strftime("%Y-%m-%d"),
            'notes': self.notes_area.toPlainText(),
            'total': self.lbl_total.text().replace("Total: ₱", "").replace(",", "")
        }
        
        self.confirm_reservation_requested.emit(reservation_data)

    def handle_check_in(self):
        row = self.table.currentRow()
        if row >= 0:
            reservation_id_item = self.table.item(row, 0)
            if reservation_id_item:
                reservation_id = reservation_id_item.text().strip()
                if reservation_id:
                    status = self.get_table_value(row, 7)
                    if status == "CONFIRMED":
                        if self.confirm_action("Check In", "Check in this guest?"):
                            self.check_in_requested.emit(reservation_id)
                    else:
                        self.show_error(f"Cannot check in reservation with status: {status}")
                else:
                    self.show_error("Invalid reservation ID.")
            else:
                self.show_error("Could not get reservation ID.")
        else:
            self.show_error("Please select a reservation.")

    def handle_check_out(self):
        row = self.table.currentRow()
        if row >= 0:
            reservation_id_item = self.table.item(row, 0)
            if reservation_id_item:
                reservation_id = reservation_id_item.text().strip()
                if reservation_id:
                    status = self.get_table_value(row, 7)
                    if status == "CHECKED_IN":
                        if self.confirm_action("Check Out", "Check out this guest?"):
                            self.check_out_requested.emit(reservation_id)
                    else:
                        self.show_error(f"Cannot check out reservation with status: {status}")
                else:
                    self.show_error("Invalid reservation ID.")
            else:
                self.show_error("Could not get reservation ID.")
        else:
            self.show_error("Please select a reservation.")

    def handle_cancel_reservation(self):  # ADDED
        """Handle cancel reservation button click"""
        row = self.table.currentRow()
        if row >= 0:
            reservation_id_item = self.table.item(row, 0)
            if reservation_id_item:
                reservation_id = reservation_id_item.text().strip()
                if reservation_id:
                    status = self.get_table_value(row, 7)
                    if status in ["CONFIRMED", "CHECKED_IN"]:
                        if self.confirm_action("Cancel Reservation", "Are you sure you want to cancel this reservation?"):
                            self.cancel_reservation_requested.emit(reservation_id)
                    else:
                        self.show_error(f"Cannot cancel reservation with status: {status}")
                else:
                    self.show_error("Invalid reservation ID.")
            else:
                self.show_error("Could not get reservation ID.")
        else:
            self.show_error("Please select a reservation.")

    def handle_delete_reservation(self):
        """Handle delete reservation button click - only allowed for CANCELLED or CHECKED_OUT"""
        row = self.table.currentRow()
        if row >= 0:
            reservation_id_item = self.table.item(row, 0)
            if reservation_id_item:
                reservation_id = reservation_id_item.text().strip()
                if reservation_id:
                    status = self.get_table_value(row, 7)
                    if status in ["CANCELLED", "CHECKED_OUT"]:
                        if self.confirm_action("Delete Reservation", "This will permanently delete the reservation. Are you sure?"):
                            self.delete_reservation_requested.emit(reservation_id)
                    else:
                        self.show_error(f"Cannot delete reservation with status: {status}. Only CANCELLED or CHECKED_OUT reservations can be deleted.")
                else:
                    self.show_error("Invalid reservation ID.")
            else:
                self.show_error("Could not get reservation ID.")
        else:
            self.show_error("Please select a reservation.")

    def handle_refresh(self):
        self.refresh_requested.emit()

    def handle_filter(self, status):
        self.filter_requested.emit(status)

    # ── Public Methods ──────────────────────────────────────────────────────
    def load_guests(self, guests: list):
        """Load guests into combo box - handles both name formats"""
        self.guest_combo.clear()
        for g in guests:
            if 'first_name' in g and 'last_name' in g:
                display_name = f"{g.get('first_name', '')} {g.get('last_name', '')}".strip()
            elif 'name' in g:
                display_name = g.get('name', '')
            else:
                display_name = "Unknown Guest"
            
            guest_id = g.get('id') or g.get('guest_id')
            self.guest_combo.addItem(display_name, guest_id)

    def load_rooms(self, rooms: list):
        """Load available rooms into combo box"""
        self.room_combo.clear()
        if not rooms:
            return
        
        for r in rooms:
            room_id = r.get('id') or r.get('room_id')
            room_number = r.get('room_number', '')
            room_type = r.get('room_type', '')
            price = r.get('price', 0)
            
            try:
                price_float = float(price)
                display_name = f"{room_number} - {room_type} - ₱{price_float:,.2f}"
            except (ValueError, TypeError):
                display_name = f"{room_number} - {room_type}"
            
            self.room_combo.addItem(display_name, room_id)

    def load_reservations(self, reservations: list):
        """Load reservations into table"""
        self.table.setRowCount(0)
        
        if not reservations:
            return
        
        for r in reservations:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)
            
            # Get the reservation ID - the model returns it as 'id'
            reservation_id = str(r.get("id", r.get("reservation_id", "")))
            
            # Column 0: ID (hidden)
            id_item = QTableWidgetItem(reservation_id)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 0, id_item)
            
            # Column 1: Guest Name
            guest_name = r.get("guest_name", "")
            guest_item = QTableWidgetItem(str(guest_name))
            guest_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 1, guest_item)
            
            # Column 2: Room Number
            room_number = r.get("room_number", "")
            room_item = QTableWidgetItem(str(room_number))
            room_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 2, room_item)
            
            # Column 3: Check-In
            check_in = r.get("check_in", "")
            check_in_item = QTableWidgetItem(str(check_in))
            check_in_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 3, check_in_item)
            
            # Column 4: Check-Out
            check_out = r.get("check_out", "")
            check_out_item = QTableWidgetItem(str(check_out))
            check_out_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 4, check_out_item)
            
            # Column 5: Nights
            nights = r.get("nights", "")
            nights_item = QTableWidgetItem(str(nights))
            nights_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 5, nights_item)
            
            # Column 6: Total
            total = r.get("total", r.get("total_price", "0"))
            if total:
                try:
                    total_formatted = f"₱{float(total):,.2f}"
                except (ValueError, TypeError):
                    total_formatted = str(total)
            else:
                total_formatted = "₱0.00"
            total_item = QTableWidgetItem(total_formatted)
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 6, total_item)
            
            # Column 7: Status
            status = r.get("status", "")
            status_item = QTableWidgetItem(str(status))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 7, status_item)

    def set_total(self, total: str):
        """Set the total label"""
        try:
            total_float = float(total)
            self.lbl_total.setText(f"Total: ₱{total_float:,.2f}")
        except (ValueError, TypeError):
            self.lbl_total.setText(f"Total: ₱{total}")

    def clear_form(self):
        """Clear reservation form"""
        self.check_in_date = None
        self.check_out_date = None
        self.check_in_field.clear()
        self.check_out_field.clear()
        self.notes_area.clear()
        self.room_combo.clear()
        self.set_total("0.00")

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""

    def confirm_action(self, title: str, message: str) -> bool:
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def show_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)


__all__ = ['ReservationPanel']


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = ReservationPanel()
    w.resize(1200, 750)
    w.show()
    sys.exit(app.exec())