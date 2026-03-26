# ServicesPanel.py - Simplified version
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, 
    QAbstractItemView, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QCursor


class ServicesPanel(QWidget):
    def __init__(self):
        super().__init__()
        print("ServicesPanel initialized")
        self.init_ui()
    
    def init_ui(self):
        self.setObjectName("service_root")
        self.setStyleSheet("QWidget#service_root { background-color: #2F2038; border: none; }")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Top panel
        top_panel = QFrame()
        top_panel.setStyleSheet("background-color: #3D2850; border-radius: 6px;")
        top_panel.setFixedHeight(200)
        top_layout = QHBoxLayout(top_panel)
        
        # Center label
        label = QLabel("Services Panel - Coming Soon!")
        label.setFont(QFont("Segoe UI", 14))
        label.setStyleSheet("color: #FFE0E3;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(label)
        
        main_layout.addWidget(top_panel)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Service Name", "Price", "Duration"])
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
            {"id": 1, "name": "Spa Massage", "price": "1500.00", "duration": "60 mins"},
            {"id": 2, "name": "Gym Session", "price": "500.00", "duration": "120 mins"},
            {"id": 3, "name": "Room Service", "price": "300.00", "duration": "30 mins"},
        ]
        
        self.table.setRowCount(0)
        for item in sample_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(item["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(item["price"]))
            self.table.setItem(row, 3, QTableWidgetItem(item["duration"]))


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ServicesPanel()
    window.resize(1100, 750)
    window.show()
    sys.exit(app.exec())