import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, 
    QHBoxLayout, QVBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QSizePolicy, QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor


class RoomPanel(QWidget):
    
    # Signal definitions for controller communication
    add_room_requested = pyqtSignal(dict)
    edit_room_requested = pyqtSignal(dict)
    update_status_requested = pyqtSignal(str, str)
    refresh_requested = pyqtSignal()
    clear_form_requested = pyqtSignal()
    
    def __init__(self): 
        super().__init__()
        self.current_room_id = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.static_rooms = []
        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        self.setObjectName("room_root")
        self.setStyleSheet("QWidget#room_root { background-color: #2F2038; border: none; }")
        
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(10)

        root_layout.addWidget(self._build_form_panel())
        root_layout.addWidget(self._build_table_panel(), stretch=1)

    def _connect_signals(self):
        self.btn_add.clicked.connect(self.handle_add_room)
        self.btn_set.clicked.connect(self.handle_set_status)
        self.btn_refresh.clicked.connect(self.handle_refresh)
        self.btn_clear.clicked.connect(self.handle_clear_form)
        self.table.itemSelectionChanged.connect(self.fill_form_from_table)

    def _build_form_panel(self):
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

        p1 = self._create_sub_panel()
        lay1 = QVBoxLayout(p1)
        lay1.addWidget(self._styled_label("Room Number:*"))
        self.room_number_field = self._styled_input()
        lay1.addWidget(self.room_number_field)
        lay1.addWidget(self._styled_label("Capacity:*"))
        self.capacity_field = self._styled_input()
        lay1.addWidget(self.capacity_field)
        layout.addWidget(p1, stretch=1)

        p2 = self._create_sub_panel()
        lay2 = QVBoxLayout(p2)
        lay2.addWidget(self._styled_label("Room Type:*"))
        self.room_type_combo = QComboBox()
        self.room_type_combo.addItems(["SINGLE", "DOUBLE", "DELUXE", "SUITE"])
        self.room_type_combo.setFixedHeight(35)
        self.room_type_combo.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px; padding-left: 8px;")
        lay2.addWidget(self.room_type_combo)
        lay2.addWidget(self._styled_label("Price per Night:*"))
        self.price_field = self._styled_input()
        lay2.addWidget(self.price_field)
        layout.addWidget(p2, stretch=1)

        p3 = self._create_sub_panel()
        lay3 = QVBoxLayout(p3)
        lay3.addWidget(self._styled_label("Description / Notes:"))
        self.description_field = self._styled_input()
        lay3.addWidget(self.description_field)
        lay3.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_add = self._action_button("Add Room", "#BE3455")
        self.btn_clear = self._action_button("Clear Form", "#412B4E")
        self.btn_add.setFixedWidth(150)
        self.btn_clear.setFixedWidth(150)
        
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_clear)
        
        lay3.addLayout(btn_layout)
        lay3.addStretch()
        layout.addWidget(p3, stretch=1)

        return form_outer

    def _build_table_panel(self):
        table_outer = QFrame()
        table_outer.setObjectName("table_outer")
        table_outer.setStyleSheet("QFrame#table_outer { background-color: #2F2038; border: 1px solid #412B4E; border-radius: 6px; }")
        layout = QVBoxLayout(table_outer)
        layout.setContentsMargins(10, 10, 10, 10)

        tools = QHBoxLayout()
        tools.addWidget(self._styled_label("Update Status:"))
        self.room_status_combo = QComboBox()
        self.room_status_combo.addItems(["AVAILABLE", "OCCUPIED", "MAINTENANCE"])
        self.room_status_combo.setFixedWidth(150)
        self.room_status_combo.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px;")
        tools.addWidget(self.room_status_combo)

        self.btn_set = self._action_button("Set Status", "#412B4E")
        self.btn_refresh = self._action_button("Refresh", "#412B4E")
        
        tools.addWidget(self.btn_set)
        tools.addWidget(self.btn_refresh)
        tools.addStretch()
        layout.addLayout(tools)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Room No", "Type", "Price", "Cap", "Status", "Desc"])
        self.table.setColumnHidden(0, True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
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

    def _create_sub_panel(self):
        p = QFrame()
        p.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        return p

    def _styled_label(self, t):
        l = QLabel(t)
        l.setStyleSheet("color: #FFE0E3; background: transparent; font-size: 11pt;")
        l.setFont(QFont("Segoe UI Semilight", 11))
        return l

    def _styled_input(self):
        e = QLineEdit()
        e.setFixedHeight(35)
        e.setStyleSheet("background-color: #F9F5FF; color: #2F2038; border-radius: 4px; padding-left: 8px;")
        return e

    def _action_button(self, t, bg_color):
        b = QPushButton(t)
        b.setFixedSize(110, 34)
        b.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        b.setFont(QFont("Segoe UI Semilight", 10, QFont.Weight.Bold))
        b.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color}; color: #FFE0E3;
                border: none; border-radius: 6px;
            }}
            QPushButton:hover {{ background-color: #5A3D6B; }}
        """)
        return b

    def handle_add_room(self):
        if not self.room_number_field.text():
            self.show_error("Room number is required.")
            return
        
        if not self.price_field.text():
            self.show_error("Price is required.")
            return
        
        if not self.capacity_field.text():
            self.show_error("Capacity is required.")
            return
        
        price_text = self.price_field.text().strip()
        price_text = price_text.replace("₱", "").replace(",", "").strip()
        
        room_data = {
            'room_number': self.room_number_field.text(),
            'room_type': self.room_type_combo.currentText(),
            'price': price_text,
            'capacity': self.capacity_field.text(),
            'description': self.description_field.text()
        }
        
        if self.current_room_id:
            room_data['id'] = self.current_room_id
            self.edit_room_requested.emit(room_data)
        else:
            self.add_room_requested.emit(room_data)

    def handle_set_status(self):
        row = self.get_selected_row()
        if row >= 0:
            room_id_item = self.table.item(row, 0)
            if room_id_item:
                room_id = room_id_item.text().strip()
                if room_id:
                    new_status = self.room_status_combo.currentText()
                    self.update_status_requested.emit(room_id, new_status)
                else:
                    self.show_error("Invalid room ID.")
            else:
                self.show_error("Could not get room ID.")
        else:
            self.show_error("Please select a room to update status.")

    def handle_refresh(self):
        self.refresh_requested.emit()

    def handle_clear_form(self):
        self.current_room_id = None
        self.btn_add.setText("Add Room")
        self._clear_form_fields()

    def fill_form_from_table(self):
        row = self.get_selected_row()
        if row >= 0:
            room_id_item = self.table.item(row, 0)
            if room_id_item:
                self.current_room_id = room_id_item.text().strip()
                
                room_number_item = self.table.item(row, 1)
                self.room_number_field.setText(room_number_item.text() if room_number_item else "")
                
                room_type_item = self.table.item(row, 2)
                room_type = room_type_item.text() if room_type_item else "SINGLE"
                self.room_type_combo.setCurrentText(room_type)
                
                price_item = self.table.item(row, 3)
                if price_item:
                    price_text = price_item.text().replace("₱", "").replace(",", "").strip()
                    self.price_field.setText(price_text)
                else:
                    self.price_field.setText("")
                
                capacity_item = self.table.item(row, 4)
                self.capacity_field.setText(capacity_item.text() if capacity_item else "")
                
                status_item = self.table.item(row, 5)
                status = status_item.text() if status_item else "AVAILABLE"
                self.room_status_combo.setCurrentText(status)
                
                desc_item = self.table.item(row, 6)
                self.description_field.setText(desc_item.text() if desc_item else "")
                
                self.btn_add.setText("Update Room")

    def _clear_form_fields(self):
        self.room_number_field.clear()
        self.price_field.clear()
        self.capacity_field.clear()
        self.description_field.clear()
        self.room_type_combo.setCurrentIndex(0)
        self.room_status_combo.setCurrentIndex(0)
        self.current_room_id = None
        self.btn_add.setText("Add Room")
        self.table.clearSelection()

    def load_rooms(self, rooms: list):
        self.static_rooms = rooms
        self.table.setRowCount(0)
        
        if not rooms:
            return
        
        for r in rooms:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setRowHeight(row, 40)
            
            room_id = str(r.get("room_id", r.get("id", "")))
            
            id_item = QTableWidgetItem(room_id)
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 0, id_item)
            
            room_number = r.get("room_number", "")
            number_item = QTableWidgetItem(str(room_number))
            number_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 1, number_item)
            
            room_type = r.get("room_type", "")
            type_item = QTableWidgetItem(str(room_type))
            type_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 2, type_item)
            
            price = r.get("price", "0")
            try:
                price_float = float(price)
                price_formatted = f"₱{price_float:,.2f}"
            except (ValueError, TypeError):
                price_formatted = str(price)
            price_item = QTableWidgetItem(price_formatted)
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 3, price_item)
            
            capacity = r.get("capacity", "")
            capacity_item = QTableWidgetItem(str(capacity))
            capacity_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 4, capacity_item)
            
            status = r.get("status", "")
            status_item = QTableWidgetItem(str(status))
            status_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 5, status_item)
            
            description = r.get("description", "")
            desc_item = QTableWidgetItem(str(description))
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.table.setItem(row, 6, desc_item)

    def get_selected_row(self) -> int:
        return self.table.currentRow()

    def get_table_value(self, row: int, col: int) -> str:
        item = self.table.item(row, col)
        return item.text() if item else ""

    def show_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RoomPanel()
    window.resize(1100, 750)
    window.show()
    sys.exit(app.exec())