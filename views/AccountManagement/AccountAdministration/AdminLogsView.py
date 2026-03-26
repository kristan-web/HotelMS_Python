import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton, QComboBox, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QHBoxLayout,
    QHeaderView, QAbstractItemView, QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor, QColor, QBrush


class AdminLogsView(QWidget):
    """
    Admin Audit Logs View.
    Displays all audit log entries with optional filtering by Action and Table.
    """
    
    # Signal to navigate back
    back_requested = pyqtSignal()
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Admin – Audit Logs")
        self.setMinimumSize(1100, 640)
        self.all_logs = []  # Store all logs for filtering
        self._build_ui()
        
    def _build_ui(self):
        self.setObjectName("logs_root")
        self.setStyleSheet("""
            QWidget#logs_root {
                background-color: #2F2038;
                border: none;
            }
        """)
        
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        
        root.addWidget(self._build_header_panel())
        root.addWidget(self._build_center_panel())
    
    def _build_header_panel(self):
        header = QWidget()
        header.setObjectName("logs_header")
        header.setStyleSheet("""
            QWidget#logs_header {
                background-color: #FFE0E3;
                border: none;
            }
        """)
        header.setFixedHeight(70)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(22, 14, 22, 14)
        
        # Title
        title = QLabel("Audit Logs")
        title.setFont(QFont("Segoe UI Semilight", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2F2038; background: transparent;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Right panel with status and back button
        right_panel = QWidget()
        right_panel.setStyleSheet("background: transparent;")
        right_layout = QHBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)
        
        self.status_label = QLabel("Loading…")
        self.status_label.setFont(QFont("Segoe UI Semilight", 13))
        self.status_label.setStyleSheet("color: #2F2038; background: transparent;")
        right_layout.addWidget(self.status_label)
        
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        self.back_btn.setFixedSize(100, 32)
        self.back_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2F2038;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 12px;
            }
            QPushButton:hover {
                background-color: #412B4E;
            }
        """)
        self.back_btn.clicked.connect(self.go_back)
        right_layout.addWidget(self.back_btn)
        
        layout.addWidget(right_panel)
        
        return header
    
    def _build_center_panel(self):
        center = QWidget()
        center.setStyleSheet("background-color: #2F2038;")
        
        layout = QVBoxLayout(center)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(8)
        
        layout.addWidget(self._build_filter_panel())
        layout.addWidget(self._build_table_panel())
        
        return center
    
    def _build_filter_panel(self):
        filter_bar = QWidget()
        filter_bar.setStyleSheet("background-color: #2F2038;")
        
        layout = QHBoxLayout(filter_bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Action filter
        action_label = QLabel("Filter by Action:")
        action_label.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        action_label.setStyleSheet("color: #FFE0E3;")
        layout.addWidget(action_label)
        
        self.action_filter = QComboBox()
        self.action_filter.addItems(["ALL", "INSERT", "UPDATE", "DELETE"])
        self.action_filter.setFont(QFont("Segoe UI Semilight", 12))
        self.action_filter.setFixedHeight(32)
        self.action_filter.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.action_filter.setStyleSheet("""
            QComboBox {
                background-color: #FFE0E3;
                color: #2F2038;
                border: 1px solid #BE3455;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QComboBox:hover {
                background-color: #F0C8C0;
                border: 1px solid #A02848;
            }
            QComboBox::drop-down {
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2F2038;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: #FFE0E3;
                color: #2F2038;
                selection-background-color: #BE3455;
                selection-color: #FFE0E3;
                border: 1px solid #BE3455;
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F0C8C0;
                color: #2F2038;
            }
        """)
        self.action_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.action_filter)
        
        layout.addSpacing(18)
        
        # Table filter
        table_label = QLabel("Filter by Table:")
        table_label.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        table_label.setStyleSheet("color: #FFE0E3;")
        layout.addWidget(table_label)
        
        self.table_filter = QComboBox()
        self.table_filter.setFont(QFont("Segoe UI Semilight", 12))
        self.table_filter.setFixedHeight(32)
        self.table_filter.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.table_filter.setStyleSheet("""
            QComboBox {
                background-color: #FFE0E3;
                color: #2F2038;
                border: 1px solid #BE3455;
                border-radius: 6px;
                padding: 4px 12px;
                font-weight: bold;
            }
            QComboBox:hover {
                background-color: #F0C8C0;
                border: 1px solid #A02848;
            }
            QComboBox::drop-down {
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #2F2038;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: #FFE0E3;
                color: #2F2038;
                selection-background-color: #BE3455;
                selection-color: #FFE0E3;
                border: 1px solid #BE3455;
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 6px 12px;
                font-weight: bold;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F0C8C0;
                color: #2F2038;
            }
        """)
        self.table_filter.currentTextChanged.connect(self.apply_filters)
        layout.addWidget(self.table_filter)
        
        layout.addSpacing(18)
        
        # Refresh button
        self.refresh_btn = QPushButton("↺  Refresh")
        self.refresh_btn.setFont(QFont("Segoe UI Semilight", 13, QFont.Weight.Bold))
        self.refresh_btn.setFixedHeight(32)
        self.refresh_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #BE3455;
                color: #FFE0E3;
                border: none;
                border-radius: 6px;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #A02848;
            }
        """)
        self.refresh_btn.clicked.connect(self.apply_filters)
        layout.addWidget(self.refresh_btn)
        
        layout.addStretch()
        
        return filter_bar
    
    def _build_table_panel(self):
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Log ID", "Table", "Record ID", "Action", 
            "Changed By", "Timestamp", "Old Values", "New Values"
        ])
        
        # Hide Log ID column
        self.table.setColumnHidden(0, True)
        
        self.table.setFont(QFont("Segoe UI Semilight", 12))
        self.table.verticalHeader().setDefaultSectionSize(32)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setShowGrid(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #3D2850;
                color: #F2F2F2;
                border: 2px solid #412B4E;
                border-radius: 6px;
                gridline-color: transparent;
            }
            QTableWidget::item {
                padding: 4px 8px;
            }
            QTableWidget::item:hover {
                background-color: #BE3455;
                color: #FFE0E3;
            }
            QTableWidget::item:selected {
                background-color: #BE3455;
                color: #FFE0E3;
            }
            
            QHeaderView::section {
                background-color: #412B4E;
                color: #FFE0E3;
                font-weight: bold;
                padding: 8px;
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
        """)
        
        # Style the vertical header
        self.table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #412B4E;
                color: #FFE0E3;
                font-weight: bold;
                padding: 8px;
                border: none;
                border-right: 1px solid #2F2038;
                border-bottom: 1px solid #2F2038;
            }
        """)
        
        # Set column widths
        self.table.setColumnWidth(1, 110)   # Table
        self.table.setColumnWidth(2, 80)    # Record ID
        self.table.setColumnWidth(3, 80)    # Action
        self.table.setColumnWidth(4, 140)   # Changed By
        self.table.setColumnWidth(5, 155)   # Timestamp
        self.table.setColumnWidth(6, 185)   # Old Values
        self.table.setColumnWidth(7, 185)   # New Values
        
        # Make header stretch for remaining space
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        return self.table
    
    def apply_filters(self):
        """Apply filters and refresh table"""
        action = self.action_filter.currentText()
        table = self.table_filter.currentText()
        self._load_filtered_logs(action, table)
    
    def _load_filtered_logs(self, action_filter="ALL", table_filter="ALL"):
        """Filter and load logs into table"""
        filtered = self.all_logs
        
        # Apply action filter
        if action_filter != "ALL":
            filtered = [log for log in filtered if log.get('action') == action_filter]
        
        # Apply table filter
        if table_filter != "ALL":
            filtered = [log for log in filtered if log.get('table_name') == table_filter]
        
        # Clear table
        self.table.setRowCount(0)
        
        # Add filtered logs
        for log in filtered:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Set values
            self.table.setItem(row, 0, QTableWidgetItem(str(log.get('log_id', ''))))
            self.table.setItem(row, 1, QTableWidgetItem(str(log.get('table_name', ''))))
            self.table.setItem(row, 2, QTableWidgetItem(str(log.get('record_id', ''))))
            
            # Action item with color
            action = str(log.get('action', ''))
            action_item = QTableWidgetItem(action)
            
            # Color the action based on type
            if action == "INSERT":
                action_item.setForeground(QBrush(QColor(34, 139, 34)))  # Green
                action_item.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
            elif action == "UPDATE":
                action_item.setForeground(QBrush(QColor(30, 100, 200)))  # Blue
                action_item.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
            elif action == "DELETE":
                action_item.setForeground(QBrush(QColor(200, 40, 40)))  # Red
                action_item.setFont(QFont("Segoe UI Semilight", 12, QFont.Weight.Bold))
            
            self.table.setItem(row, 3, action_item)
            self.table.setItem(row, 4, QTableWidgetItem(str(log.get('changed_by', ''))))
            self.table.setItem(row, 5, QTableWidgetItem(str(log.get('timestamp', ''))))
            self.table.setItem(row, 6, QTableWidgetItem(self._trim_json(str(log.get('old_values', '—')))))
            self.table.setItem(row, 7, QTableWidgetItem(self._trim_json(str(log.get('new_values', '—')))))
        
        # Update status
        self.status_label.setText(f"{len(filtered)} record{'s' if len(filtered) != 1 else ''} found")
    
    def load_logs(self, logs):
        """
        Load logs into view
        logs: list of dicts with keys: log_id, table_name, record_id, action, 
              changed_by, timestamp, old_values, new_values
        """
        self.all_logs = logs
        self._load_filtered_logs(self.action_filter.currentText(), self.table_filter.currentText())
    
    def load_table_options(self, tables):
        """Load table filter options"""
        self.table_filter.clear()
        self.table_filter.addItem("ALL")
        for table in tables:
            self.table_filter.addItem(table)
    
    def _trim_json(self, text: str, max_len=60) -> str:
        """Truncate long JSON strings"""
        if text == "—" or text == "None" or not text:
            return "—"
        if len(text) > max_len:
            return text[:max_len - 3] + "…"
        return text
    
    def go_back(self):
        """Navigate back to dashboard"""
        if self.main_window:
            self.main_window.show()
        self.close()
    
    def show_error(self, msg: str):
        QMessageBox.warning(self, "Error", msg)
    
    def show_message(self, title: str, msg: str):
        QMessageBox.information(self, title, msg)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    w = AdminLogsView()
    
    # Sample data for testing (list of dictionaries)
    sample_logs = [
        {"log_id": 1, "table_name": "Guests", "record_id": "G001", "action": "INSERT", 
         "changed_by": "admin@hotel.com", "timestamp": "2024-01-15 10:30:00", 
         "old_values": "—", "new_values": '{"name":"John Doe","email":"john@email.com"}'},
        {"log_id": 2, "table_name": "Services", "record_id": "S001", "action": "UPDATE", 
         "changed_by": "admin@hotel.com", "timestamp": "2024-01-15 11:45:00", 
         "old_values": '{"price":500}', "new_values": '{"price":550}'},
        {"log_id": 3, "table_name": "Bookings", "record_id": "B001", "action": "DELETE", 
         "changed_by": "staff@hotel.com", "timestamp": "2024-01-15 14:20:00", 
         "old_values": '{"status":"confirmed"}', "new_values": "—"},
    ]
    
    w.load_table_options(["Guests", "Services", "Bookings", "Rooms"])
    w.load_logs(sample_logs)
    w.show()
    sys.exit(app.exec())