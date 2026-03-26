# ReservationPanel.py - Simplified version
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


class ReservationPanel(QWidget):
    def __init__(self):
        super().__init__()
        print("ReservationPanel initialized")
        self.init_ui()
    
    def init_ui(self):
        self.setObjectName("res_root")
        self.setStyleSheet("QWidget#res_root { background-color: #2F2038; border: none; }")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top panel
        top_panel = QFrame()
        top_panel.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        top_panel.setFixedHeight(200)
        top_layout = QHBoxLayout(top_panel)
        
        # Center label
        label = QLabel("Reservation Panel - Coming Soon!")
        label.setFont(QFont("Segoe UI", 14))
        label.setStyleSheet("color: #FFE0E3;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(label)
        
        main_layout.addWidget(top_panel)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Guest", "Room", "Check-In", "Check-Out", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850;
                color: #F2F2F2;
                gridline-color: #412B4E;
            }
        """)
        main_layout.addWidget(self.table)
        
        # Load sample data
        self.load_sample_data()
    
    def load_sample_data(self):
        sample_data = [
            {"id": 1, "guest": "John Doe", "room": "101", "check_in": "2024-01-01", "check_out": "2024-01-05", "status": "CONFIRMED"},
            {"id": 2, "guest": "Jane Smith", "room": "202", "check_in": "2024-01-10", "check_out": "2024-01-12", "status": "CHECKED_IN"},
        ]
        
        self.table.setRowCount(0)
        for item in sample_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["guest"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["room"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["check_in"]))
            self.table.setItem(row, 4, QTableWidgetItem(item["check_out"]))
            self.table.setItem(row, 5, QTableWidgetItem(item["status"]))


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ReservationPanel()
    window.resize(1200, 750)
    window.show()
    sys.exit(app.exec())