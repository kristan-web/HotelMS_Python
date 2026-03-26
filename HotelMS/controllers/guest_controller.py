# controllers/guest_controller.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.guest_model import GuestModel


class GuestController:
    def __init__(self, db_connection):
        self.model = GuestModel(db_connection)
        self.view = None
    
    def set_view(self, view):
        self.view = view
        self._connect_signals()
        self.refresh_guest_list()
    
    def _connect_signals(self):
        if self.view:
            self.view.add_btn.clicked.connect(self.add_or_update_guest)
            self.view.clear_btn.clicked.connect(self.clear_form)
            self.view.delete_btn.clicked.connect(self.delete_guest)
            self.view.refresh_btn.clicked.connect(self.refresh_guest_list)
            self.view.table.itemSelectionChanged.connect(self.on_row_selected)
    
    def add_or_update_guest(self):
        first_name = self.view.get_first_name()
        last_name = self.view.get_last_name()
        email = self.view.get_email()
        address = self.view.get_address()
        phone = self.view.get_phone()
        
        if not all([first_name, last_name, email, phone, address]):
            self.view.show_message("Error", "All fields are required!", "warning")
            return
        
        if '@' not in email or '.' not in email:
            self.view.show_message("Error", "Invalid email address!", "warning")
            return
        
        if len(phone) < 10:
            self.view.show_message("Error", "Phone number must be at least 10 digits!", "warning")
            return
        
        if self.view.add_btn.text() == "Add Guest":
            success, message, _ = self.model.add_guest(first_name, last_name, email, phone, address)
            if success:
                self.view.show_message("Success", message, "info")
                self.clear_form()
                self.refresh_guest_list()
            else:
                self.view.show_message("Error", message, "error")
        else:
            row = self.view.get_selected_row()
            if row >= 0:
                guest_id = int(self.view.get_table_value(row, 0))
                success, message = self.model.update_guest(guest_id, first_name, last_name, email, phone, address)
                if success:
                    self.view.show_message("Success", message, "info")
                    self.clear_form()
                    self.refresh_guest_list()
                else:
                    self.view.show_message("Error", message, "error")
    
    def delete_guest(self):
        row = self.view.get_selected_row()
        if row < 0:
            self.view.show_message("Delete", "Please select a guest to delete.", "warning")
            return
        
        name = f"{self.view.get_table_value(row, 1)} {self.view.get_table_value(row, 2)}"
        if self.view.confirm_delete(name):
            guest_id = int(self.view.get_table_value(row, 0))
            success, message = self.model.delete_guest(guest_id)
            if success:
                self.view.show_message("Success", message, "info")
                self.clear_form()
                self.refresh_guest_list()
            else:
                self.view.show_message("Error", message, "error")
    
    def on_row_selected(self):
        row = self.view.get_selected_row()
        if row >= 0:
            first = self.view.get_table_value(row, 1)
            last = self.view.get_table_value(row, 2)
            email = self.view.get_table_value(row, 3)
            phone = self.view.get_table_value(row, 4)
            address = self.view.get_table_value(row, 5)
            self.view.fill_form(first, last, email, address, phone)
            self.view.set_add_btn_text("Update Guest")
    
    def clear_form(self):
        self.view.clear_form()
    
    def refresh_guest_list(self):
        guests = self.model.get_all_guests()
        self.view.load_table(guests)