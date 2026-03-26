import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.guest_model import GuestModel


class GuestController:
    """Controller class for guest operations"""
    
    def __init__(self, db_connection):
        """
        Initialize the GuestController
        
        Args:
            db_connection: MySQL database connection object
        """
        self.model = GuestModel(db_connection)
        self.view = None
        print("GuestController initialized")
    
    def set_view(self, view):
        """
        Set the view for this controller
        
        Args:
            view: GuestPanelView instance
        """
        self.view = view
        self._connect_signals()
        self.refresh_guest_list()
    
    def _connect_signals(self):
        """Connect view signals to controller methods"""
        if self.view:
            print("Connecting signals...")
            self.view.add_btn.clicked.connect(self.add_or_update_guest)
            self.view.clear_btn.clicked.connect(self.clear_form)
            self.view.delete_btn.clicked.connect(self.delete_guest)
            self.view.refresh_btn.clicked.connect(self.refresh_guest_list)
            self.view.table.itemSelectionChanged.connect(self.on_row_selected)
            
            # Connect search functionality if available
            if hasattr(self.view, 'search_input') and hasattr(self.view, 'search_timer'):
                self.view.search_input.textChanged.connect(self.on_search_changed)
                self.view.search_timer.timeout.connect(self.perform_search)
                print("Search signals connected")
    
    def add_or_update_guest(self):
        """Handle adding or updating a guest"""
        try:
            print("\n=== Add/Update Guest button clicked ===")
            
            # Get data from view
            first_name = self.view.get_first_name()
            last_name = self.view.get_last_name()
            email = self.view.get_email()
            address = self.view.get_address()
            phone = self.view.get_phone()
            
            print(f"Form data: first_name='{first_name}', last_name='{last_name}'")
            print(f"Email: '{email}', Phone: '{phone}', Address: '{address}'")
            
            # Validate input
            if not all([first_name, last_name, email, phone, address]):
                missing_fields = []
                if not first_name: missing_fields.append("First name")
                if not last_name: missing_fields.append("Last name")
                if not email: missing_fields.append("Email")
                if not phone: missing_fields.append("Phone")
                if not address: missing_fields.append("Address")
                
                error_msg = f"Missing fields: {', '.join(missing_fields)}"
                print(f"Validation failed: {error_msg}")
                self.view.show_message("Validation Error", "All fields are required!", "warning")
                return
            
            # Validate email format
            if '@' not in email or '.' not in email:
                print(f"Invalid email format: {email}")
                self.view.show_message("Validation Error", "Please enter a valid email address.", "warning")
                return
            
            # Validate phone (at least 10 digits)
            if len(phone) < 10:
                print(f"Phone number too short: {phone}")
                self.view.show_message("Validation Error", "Please enter a valid phone number (at least 10 digits).", "warning")
                return
            
            # Check if we're adding or updating
            button_text = self.view.add_btn.text()
            selected_row = self.view.get_selected_row()
            
            print(f"Button text: '{button_text}', Selected row: {selected_row}")
            
            if button_text == "Add Guest":
                print("Adding new guest...")
                success, message, guest_id = self.model.add_guest(
                    first_name, last_name, email, phone, address
                )
                
                print(f"Add result: success={success}, message='{message}', guest_id={guest_id}")
                
                if success:
                    self.view.show_message("Success", message, "info")
                    self.clear_form()
                    self.refresh_guest_list()
                else:
                    self.view.show_message("Error", message, "error")
                    
            else:  # Update Guest
                print("Updating existing guest...")
                if selected_row >= 0:
                    try:
                        guest_id = int(self.view.get_table_value(selected_row, 0))
                        print(f"Updating guest ID: {guest_id}")
                        
                        success, message = self.model.update_guest(
                            guest_id, first_name, last_name, email, phone, address
                        )
                        
                        print(f"Update result: success={success}, message='{message}'")
                        
                        if success:
                            self.view.show_message("Success", message, "info")
                            self.clear_form()
                            self.refresh_guest_list()
                        else:
                            self.view.show_message("Error", message, "error")
                    except ValueError as e:
                        print(f"ValueError: {e}")
                        self.view.show_message("Error", "Invalid guest ID.", "error")
                else:
                    print("No row selected for update")
                    self.view.show_message("Error", "No guest selected for update.", "warning")
                
        except Exception as e:
            print(f"Unexpected error in add_or_update_guest: {e}")
            import traceback
            traceback.print_exc()
            self.view.show_message("Error", f"Unexpected error: {str(e)}", "error")
    
    def delete_guest(self):
        """Handle guest deletion"""
        selected_row = self.view.get_selected_row()
        
        if selected_row < 0:
            self.view.show_message("Delete Guest", "Please select a guest to delete.", "warning")
            return
        
        # Get guest name for confirmation
        first_name = self.view.get_table_value(selected_row, 1)
        last_name = self.view.get_table_value(selected_row, 2)
        guest_name = f"{first_name} {last_name}"
        
        try:
            guest_id = int(self.view.get_table_value(selected_row, 0))
            print(f"Deleting guest: {guest_name} (ID: {guest_id})")
            
            # Confirm deletion
            if self.view.confirm_delete(guest_name):
                success, message = self.model.delete_guest(guest_id)
                
                if success:
                    self.view.show_message("Success", message, "info")
                    self.clear_form()
                    self.refresh_guest_list()
                else:
                    self.view.show_message("Error", message, "error")
        except ValueError as e:
            print(f"ValueError: {e}")
            self.view.show_message("Error", "Invalid guest ID.", "error")
    
    def on_row_selected(self):
        """Handle row selection in the table"""
        selected_row = self.view.get_selected_row()
        
        if selected_row >= 0:
            print(f"Row selected: {selected_row}")
            # Get data from selected row
            first_name = self.view.get_table_value(selected_row, 1)
            last_name = self.view.get_table_value(selected_row, 2)
            email = self.view.get_table_value(selected_row, 3)
            phone = self.view.get_table_value(selected_row, 4)
            address = self.view.get_table_value(selected_row, 5)
            
            # Fill form with selected data
            self.view.fill_form(first_name, last_name, email, address, phone)
            self.view.set_add_btn_text("Update Guest")
    
    def clear_form(self):
        """Clear the form and reset to add mode"""
        print("Clearing form...")
        self.view.clear_form()
        # Clear table selection
        if self.view.table.currentRow() >= 0:
            self.view.table.clearSelection()
    
    def refresh_guest_list(self):
        """Refresh the guest table with latest data"""
        print("Refreshing guest list...")
        guests = self.model.get_all_guests()
        self.view.load_table(guests)
        
        # Clear search input if it exists
        if hasattr(self.view, 'search_input'):
            self.view.search_input.clear()
    
    def on_search_changed(self, search_text):
        """Handle search text changes"""
        if hasattr(self.view, 'search_timer'):
            self.view.search_timer.stop()
            self.view.search_timer.start(500)
        else:
            self.perform_search()
    
    def perform_search(self):
        """Perform the actual search"""
        if hasattr(self.view, 'search_input'):
            search_text = self.view.search_input.text()
            if search_text and search_text.strip():
                print(f"Searching for: {search_text}")
                guests = self.model.search_guests(search_text.strip())
                self.view.load_table(guests)
            else:
                self.refresh_guest_list()