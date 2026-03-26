# controllers/room_controller.py
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.room_model import RoomModel


class RoomController:
    """Controller class for room operations"""
    
    def __init__(self, db_connection):
        """
        Initialize the RoomController
        
        Args:
            db_connection: MySQL database connection object
        """
        self.model = RoomModel(db_connection)
        self.view = None
        print("RoomController initialized")
    
    def set_view(self, view):
        """
        Set the view for this controller
        
        Args:
            view: RoomPanel instance
        """
        self.view = view
        self._connect_signals()
        self.refresh_room_list()
    
    def _connect_signals(self):
        """Connect view signals to controller methods"""
        if self.view:
            print("Connecting room signals...")
            self.view.btn_add.clicked.connect(self.add_or_update_room)
            self.view.btn_clear.clicked.connect(self.clear_form)
            self.view.btn_del.clicked.connect(self.delete_room)
            self.view.btn_set.clicked.connect(self.update_status)
            self.view.btn_refresh.clicked.connect(self.refresh_room_list)
            self.view.table.itemSelectionChanged.connect(self.on_row_selected)
    
    def add_or_update_room(self):
        """Handle adding or updating a room"""
        try:
            print("\n=== Add/Update Room button clicked ===")
            
            # Get data from view
            room_number = self.view.room_number_field.text().strip()
            room_type = self.view.room_type_combo.currentText()
            price = self.view.price_field.text().strip()
            capacity = self.view.capacity_field.text().strip()
            description = self.view.description_field.text().strip()
            
            print(f"Room data: {room_number}, {room_type}, {price}, {capacity}")
            
            # Validate input
            if not room_number:
                self.view.show_message("Validation Error", "Room number is required!", "warning")
                return
            
            if not price:
                self.view.show_message("Validation Error", "Price is required!", "warning")
                return
            
            if not capacity:
                self.view.show_message("Validation Error", "Capacity is required!", "warning")
                return
            
            try:
                float(price)
                int(capacity)
            except ValueError:
                self.view.show_message("Validation Error", "Price must be a number and capacity must be an integer!", "warning")
                return
            
            # Check if we're adding or updating
            button_text = self.view.btn_add.text()
            selected_row = self.view.get_selected_row()
            
            if button_text == "Add Room":
                print("Adding new room...")
                success, message, room_id = self.model.add_room(
                    room_number, room_type, price, capacity, description
                )
                
                if success:
                    self.view.show_message("Success", message, "info")
                    self.clear_form()
                    self.refresh_room_list()
                else:
                    self.view.show_message("Error", message, "error")
                    
            else:  # Update Room
                print("Updating existing room...")
                if selected_row >= 0:
                    try:
                        room_id = int(self.view.get_table_value(selected_row, 0))
                        status = self.view.get_table_value(selected_row, 5)
                        
                        success, message = self.model.update_room(
                            room_id, room_number, room_type, price, capacity, status, description
                        )
                        
                        if success:
                            self.view.show_message("Success", message, "info")
                            self.clear_form()
                            self.refresh_room_list()
                        else:
                            self.view.show_message("Error", message, "error")
                    except ValueError as e:
                        print(f"ValueError: {e}")
                        self.view.show_message("Error", "Invalid room ID.", "error")
                else:
                    self.view.show_message("Error", "No room selected for update.", "warning")
                
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            self.view.show_message("Error", f"Unexpected error: {str(e)}", "error")
    
    def update_status(self):
        """Handle room status update"""
        selected_row = self.view.get_selected_row()
        
        if selected_row < 0:
            self.view.show_message("Update Status", "Please select a room to update status.", "warning")
            return
        
        try:
            room_id = int(self.view.get_table_value(selected_row, 0))
            new_status = self.view.room_status_combo.currentText()
            
            print(f"Updating room {room_id} status to {new_status}")
            
            success, message = self.model.update_room_status(room_id, new_status)
            
            if success:
                self.view.show_message("Success", message, "info")
                self.refresh_room_list()
            else:
                self.view.show_message("Error", message, "error")
                
        except Exception as e:
            print(f"Error: {e}")
            self.view.show_message("Error", f"Error: {str(e)}", "error")
    
    def delete_room(self):
        """Handle room deletion"""
        selected_row = self.view.get_selected_row()
        
        if selected_row < 0:
            self.view.show_message("Delete Room", "Please select a room to delete.", "warning")
            return
        
        # Get room info for confirmation
        room_number = self.view.get_table_value(selected_row, 1)
        
        try:
            room_id = int(self.view.get_table_value(selected_row, 0))
            
            # Confirm deletion
            reply = self.view.confirm_delete(room_number)
            if reply:
                success, message = self.model.delete_room(room_id)
                
                if success:
                    self.view.show_message("Success", message, "info")
                    self.clear_form()
                    self.refresh_room_list()
                else:
                    self.view.show_message("Error", message, "error")
                    
        except Exception as e:
            print(f"Error: {e}")
            self.view.show_message("Error", f"Error: {str(e)}", "error")
    
    def on_row_selected(self):
        """Handle row selection in the table"""
        selected_row = self.view.get_selected_row()
        
        if selected_row >= 0:
            print(f"Room row selected: {selected_row}")
            # Get data from selected row
            room_number = self.view.get_table_value(selected_row, 1)
            room_type = self.view.get_table_value(selected_row, 2)
            price = self.view.get_table_value(selected_row, 3)
            capacity = self.view.get_table_value(selected_row, 4)
            status = self.view.get_table_value(selected_row, 5)
            description = self.view.get_table_value(selected_row, 6)
            
            # Fill form with selected data
            self.view.room_number_field.setText(room_number)
            self.view.room_type_combo.setCurrentText(room_type)
            self.view.price_field.setText(price)
            self.view.capacity_field.setText(capacity)
            self.view.room_status_combo.setCurrentText(status)
            self.view.description_field.setText(description)
            self.view.btn_add.setText("Update Room")
    
    def clear_form(self):
        """Clear the form and reset to add mode"""
        print("Clearing room form...")
        self.view.clearForm()
        self.view.btn_add.setText("Add Room")
    
    def refresh_room_list(self):
        """Refresh the room table with latest data"""
        print("Refreshing room list...")
        rooms = self.model.get_all_rooms()
        self.view.load_rooms(rooms)