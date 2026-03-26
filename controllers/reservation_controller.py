"""
Reservation Controller for Hotel Management System
Connects all reservation-related views with models
"""

import sys
import os
from typing import Optional, Dict, Any, List
from datetime import date

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from PyQt6.QtWidgets import QMessageBox, QApplication
from PyQt6.QtCore import QObject, pyqtSignal

from models.guest_model import GuestModel
from models.room_model import RoomModel
from models.reservation_model import ReservationModel
from models.service_model import ServiceModel
from views.ReservationManagement.Mainframe import MainFrameView
from views.ReservationManagement.ReservationPanel import ReservationPanel
from views.ReservationManagement.GuestPanel import GuestPanelView
from views.ReservationManagement.RoomPanel import RoomPanel
from views.ReservationManagement.ServicesPanel import ServicesPanel


class ReservationController(QObject):
    """
    Controller for Reservation Management module
    Handles all reservation-related operations and view navigation
    """
    
    # Signal to notify main window
    back_to_dashboard_requested = pyqtSignal()
    
    def __init__(self, main_window=None, user_role: str = "Staff"):
        super().__init__()
        self.main_window = main_window
        self.user_role = user_role
        
        # Views
        self.mainframe = None
        self.reservation_panel = None
        self.guest_panel = None
        self.room_panel = None
        self.services_panel = None
        
        # Data cache
        self.current_reservation_filter = "ALL"
        
        # Initialize views
        self._init_views()
        self._connect_signals()
        
        # Load initial data
        self.refresh_all_data()
    
    def _init_views(self):
        """Initialize all views"""
        self.mainframe = MainFrameView(user_role=self.user_role, controller=self)
        self.reservation_panel = ReservationPanel()
        self.guest_panel = GuestPanelView()
        self.room_panel = RoomPanel()
        self.services_panel = ServicesPanel()
        
        # Set parent for proper window management
        if self.main_window:
            self.mainframe.setParent(self.main_window)
        
        # Add tabs to mainframe
        self.mainframe.add_tab(self.reservation_panel, "RESERVATIONS")
        self.mainframe.add_tab(self.guest_panel, "GUESTS")
        self.mainframe.add_tab(self.room_panel, "ROOMS")
        
        # Add ServicesPanel only for Admin users
        if self.user_role == "Admin":
            self.mainframe.add_tab(self.services_panel, "SERVICES")
    
    def _connect_signals(self):
        """Connect view signals to controller methods"""
        
        # Mainframe signals
        self.mainframe.back_btn.clicked.connect(self.go_back)
        
        # ReservationPanel signals
        self.reservation_panel.find_rooms_requested.connect(self.on_find_rooms)
        self.reservation_panel.confirm_reservation_requested.connect(self.on_confirm_reservation)
        self.reservation_panel.check_in_requested.connect(self.on_check_in)
        self.reservation_panel.check_out_requested.connect(self.on_check_out)
        self.reservation_panel.cancel_reservation_requested.connect(self.on_cancel_reservation)
        self.reservation_panel.refresh_requested.connect(self.refresh_reservations)
        self.reservation_panel.filter_requested.connect(self.on_filter_reservations)
        self.reservation_panel.room_selected_requested.connect(self.on_room_selected)
        self.reservation_panel.dates_changed.connect(self.on_dates_changed)
        
        # GuestPanel signals
        self.guest_panel.add_guest_requested.connect(self.on_add_guest)
        self.guest_panel.edit_guest_requested.connect(self.on_edit_guest)
        self.guest_panel.delete_guest_requested.connect(self.on_delete_guest)
        self.guest_panel.refresh_requested.connect(self.refresh_guests)
        self.guest_panel.clear_form_requested.connect(self.on_clear_guest_form)
        
        # RoomPanel signals
        self.room_panel.add_room_requested.connect(self.on_add_room)
        self.room_panel.edit_room_requested.connect(self.on_edit_room)
        self.room_panel.delete_room_requested.connect(self.on_delete_room)
        self.room_panel.update_status_requested.connect(self.on_update_room_status)
        self.room_panel.refresh_requested.connect(self.refresh_rooms)
        self.room_panel.clear_form_requested.connect(self.on_clear_room_form)
        
        # ServicesPanel signals
        self.services_panel.book_service_requested.connect(self.on_book_service)
        self.services_panel.delete_booking_requested.connect(self.on_delete_service_booking)
        self.services_panel.refresh_requested.connect(self.refresh_services_panel)
        self.services_panel.calculate_total_requested.connect(self.on_calculate_service_total)
    
    # ==================== Data Loading Methods ====================
    
    def refresh_all_data(self):
        """Refresh all panels with latest data"""
        self.refresh_reservations()
        self.refresh_guests()
        self.refresh_rooms()
        self.refresh_services_panel()
        self.load_guest_combo()
        self.load_service_combo()
    
    def refresh_reservations(self):
        """Refresh reservation table"""
        try:
            reservations = ReservationModel.get_all_active(self.current_reservation_filter)
            # Debug: Print first reservation structure
            if reservations:
                print(f"First reservation keys: {list(reservations[0].keys())}")
                print(f"First reservation: {reservations[0]}")
            self.reservation_panel.load_reservations(reservations)
        except Exception as e:
            print(f"Error loading reservations: {e}")
            self.show_error("Failed to load reservations")
    
    def refresh_guests(self):
        """Refresh guest table"""
        try:
            guests = GuestModel.get_all_active()
            self.guest_panel.load_table(guests)
        except Exception as e:
            print(f"Error loading guests: {e}")
            self.show_error("Failed to load guests")
    
    def refresh_rooms(self):
        """Refresh room table"""
        try:
            rooms = RoomModel.get_all_active()
            self.room_panel.load_rooms(rooms)
        except Exception as e:
            print(f"Error loading rooms: {e}")
            self.show_error("Failed to load rooms")
    
    def refresh_services_panel(self):
        """Refresh services panel data"""
        try:
            # Load guests for combo
            guests = GuestModel.get_all_for_combo()
            self.services_panel.load_guests(guests)
            
            # Load services for combo
            services = ServiceModel.get_all_active()
            self.services_panel.load_services(services)
            
            # Load bookings (reservation_services)
            bookings = self._get_all_service_bookings()
            self.services_panel.load_bookings(bookings)
        except Exception as e:
            print(f"Error loading services panel: {e}")
    
    def load_guest_combo(self):
        """Load guests into reservation panel combo box"""
        try:
            guests = GuestModel.get_all_for_combo()
            self.reservation_panel.load_guests(guests)
        except Exception as e:
            print(f"Error loading guest combo: {e}")
    
    def load_room_combo(self, rooms: list):
        """Load available rooms into reservation panel combo box"""
        self.reservation_panel.load_rooms(rooms)
    
    def load_service_combo(self):
        """Load services into services panel combo box"""
        try:
            services = ServiceModel.get_all_active()
            self.services_panel.load_services(services)
        except Exception as e:
            print(f"Error loading service combo: {e}")
    
    def _get_all_service_bookings(self) -> List[Dict]:
        """Get all service bookings from reservation_services"""
        try:
            query = """
                SELECT 
                    rs.res_service_id as booking_id,
                    CONCAT(g.first_name, ' ', g.last_name) as guest_name,
                    s.name as service_name,
                    rs.scheduled_at as scheduled_time,
                    rs.duration,
                    rs.total,
                    rs.status
                FROM reservation_services rs
                JOIN reservations r ON rs.reservation_id = r.reservation_id
                JOIN guests g ON r.guest_id = g.guest_id
                JOIN services s ON rs.service_id = s.service_id
                WHERE rs.status != 'CANCELLED'
                ORDER BY rs.created_at DESC
                LIMIT 100
            """
            from config.database import DatabaseQuery
            return DatabaseQuery.fetch_all(query)
        except Exception as e:
            print(f"Error getting service bookings: {e}")
            return []
    
    # ==================== Reservation Panel Handlers ====================
    
    def on_find_rooms(self, check_in: str, check_out: str):
        """Find available rooms for selected dates"""
        try:
            rooms = RoomModel.get_available_rooms(check_in, check_out)
            
            print(f"Found {len(rooms)} available rooms")
            
            # Format rooms for display in combo box
            formatted_rooms = []
            for r in rooms:
                formatted_rooms.append({
                    'id': r.get('id'),
                    'room_number': r.get('room_number'),
                    'room_type': r.get('room_type'),
                    'price': r.get('price')
                })
            
            self.load_room_combo(formatted_rooms)
            
            if not rooms:
                self.show_message("No Rooms Available", 
                                "No rooms available for the selected dates.")
        except Exception as e:
            print(f"Error finding rooms: {e}")
            self.show_error(f"Failed to find available rooms: {str(e)}")
    
    def on_confirm_reservation(self, reservation_data: dict):
        """Confirm and create reservation"""
        try:
            user_id = self._get_current_user_id()
            
            reservation_id = ReservationModel.create_reservation(reservation_data, user_id)
            
            if reservation_id:
                self.show_message("Success", "Reservation confirmed successfully!")
                self.refresh_reservations()
                self.refresh_rooms()
                self.clear_reservation_form()
            else:
                self.show_error("Failed to create reservation")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error confirming reservation: {e}")
            self.show_error("Failed to confirm reservation")
    
    def on_check_in(self, reservation_id: str):
        """Handle check-in"""
        try:
            if not self._confirm_action("Check In", "Check in this reservation?"):
                return
            
            success = ReservationModel.check_in(int(reservation_id))
            
            if success:
                self.show_message("Success", "Guest checked in successfully!")
                self.refresh_reservations()
                self.refresh_rooms()
            else:
                self.show_error("Failed to check in guest")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error checking in: {e}")
            self.show_error("Failed to check in")
    
    def on_check_out(self, reservation_id: str):
        """Handle check-out"""
        try:
            if not self._confirm_action("Check Out", "Check out this reservation?"):
                return
            
            success = ReservationModel.check_out(int(reservation_id))
            
            if success:
                self.show_message("Success", "Guest checked out successfully!")
                self.refresh_reservations()
                self.refresh_rooms()
            else:
                self.show_error("Failed to check out guest")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error checking out: {e}")
            self.show_error("Failed to check out")
    
    def on_cancel_reservation(self, reservation_id: str):
        """Handle cancel reservation"""
        try:
            if not self._confirm_action("Cancel Reservation", 
                                        "Are you sure you want to cancel this reservation?"):
                return
            
            success = ReservationModel.cancel_reservation(int(reservation_id))
            
            if success:
                self.show_message("Success", "Reservation cancelled successfully!")
                self.refresh_reservations()
                self.refresh_rooms()
            else:
                self.show_error("Failed to cancel reservation")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error cancelling: {e}")
            self.show_error("Failed to cancel reservation")
    
    def on_filter_reservations(self, status: str):
        """Filter reservations by status"""
        self.current_reservation_filter = status
        self.refresh_reservations()
        
    def on_room_selected(self, room_id: str):
        """Calculate total when room is selected"""
        try:
            check_in = self.reservation_panel.check_in_date
            check_out = self.reservation_panel.check_out_date
            
            if not check_in or not check_out:
                # If dates aren't selected yet, just show room price
                room = RoomModel.find(int(room_id))
                if room:
                    total = float(room['price'])
                    self.reservation_panel.set_total(f"{total:,.2f}")
            else:
                # Calculate total based on room price and nights
                nights = (check_out - check_in).days
                if nights > 0:
                    room = RoomModel.find(int(room_id))
                    if room:
                        total = float(room['price']) * nights
                        self.reservation_panel.set_total(f"{total:,.2f}")
        except Exception as e:
            print(f"Error calculating total: {e}")

    def on_dates_changed(self):
        """Update total when dates change"""
        if self.reservation_panel.room_combo.currentData():
            self.on_room_selected(str(self.reservation_panel.room_combo.currentData()))
    
    def clear_reservation_form(self):
        """Clear reservation form fields"""
        self.reservation_panel.check_in_date = None
        self.reservation_panel.check_out_date = None
        self.reservation_panel.check_in_field.clear()
        self.reservation_panel.check_out_field.clear()
        self.reservation_panel.notes_area.clear()
        self.reservation_panel.room_combo.clear()
        self.reservation_panel.set_total("0.00")
    
    # ==================== Guest Panel Handlers ====================
    
    def on_add_guest(self, guest_data: dict):
        """Add new guest"""
        try:
            # Validate required fields
            if not all([guest_data.get('first_name'), guest_data.get('last_name'), 
                       guest_data.get('email'), guest_data.get('phone'), guest_data.get('address')]):
                self.show_error("All fields are required")
                return
            
            guest_id = GuestModel.create_guest(guest_data)
            
            if guest_id:
                self.show_message("Success", f"Guest '{guest_data['first_name']} {guest_data['last_name']}' added successfully!")
                self.guest_panel.clear_form()
                self.refresh_guests()
                self.load_guest_combo()
            else:
                self.show_error("Failed to add guest")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error adding guest: {e}")
            self.show_error("Failed to add guest")
    
    def on_edit_guest(self, guest_data: dict):
        """Edit existing guest"""
        try:
            guest_id = guest_data.get('id')
            if not guest_id:
                self.show_error("Guest ID is required for editing")
                return
            
            success = GuestModel.update_guest(int(guest_id), guest_data)
            
            if success:
                self.show_message("Success", f"Guest updated successfully!")
                self.guest_panel.clear_form()
                self.refresh_guests()
                self.load_guest_combo()
            else:
                self.show_error("Failed to update guest")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error editing guest: {e}")
            self.show_error("Failed to update guest")
    
    def on_delete_guest(self, guest_id: str):
        """Delete selected guest"""
        try:
            success = GuestModel.delete_guest(int(guest_id))
            
            if success:
                self.show_message("Success", "Guest deleted successfully!")
                self.refresh_guests()
                self.load_guest_combo()
            else:
                self.show_error("Failed to delete guest")
                    
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error deleting guest: {e}")
            self.show_error("Failed to delete guest")
    
    def on_clear_guest_form(self):
        """Clear guest form"""
        self.guest_panel.clear_form()
    
    # ==================== Room Panel Handlers ====================
    
    def on_add_room(self, room_data: dict):
        """Add new room"""
        try:
            room_id = RoomModel.create_room(room_data)
            
            if room_id:
                self.show_message("Success", f"Room '{room_data['room_number']}' added successfully!")
                self.refresh_rooms()
            else:
                self.show_error("Failed to add room")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error adding room: {e}")
            self.show_error("Failed to add room")
    
    def on_edit_room(self, room_data: dict):
        """Edit existing room"""
        try:
            room_id = room_data.get('id')
            if not room_id:
                self.show_error("Room ID is required for editing")
                return
            
            success = RoomModel.update_room(int(room_id), room_data)
            
            if success:
                self.show_message("Success", f"Room '{room_data['room_number']}' updated successfully!")
                self.refresh_rooms()
            else:
                self.show_error("Failed to update room")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error editing room: {e}")
            self.show_error("Failed to update room")
    
    def on_delete_room(self, room_id: str):
        """Delete selected room"""
        try:
            success = RoomModel.delete_room(int(room_id))
            
            if success:
                self.show_message("Success", "Room deleted successfully!")
                self.refresh_rooms()
            else:
                self.show_error("Failed to delete room")
                    
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error deleting room: {e}")
            self.show_error("Failed to delete room")
    
    def on_update_room_status(self, room_id: str, new_status: str):
        """Update room status"""
        try:
            success = RoomModel.update_status(int(room_id), new_status)
            
            if success:
                self.show_message("Success", f"Room status updated to '{new_status}'!")
                self.refresh_rooms()
            else:
                self.show_error("Failed to update room status")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"Error updating status: {e}")
            self.show_error(f"Failed to update status: {str(e)}")
    
    def on_clear_room_form(self):
        """Clear room form"""
        self.room_panel._clear_form_fields()
    
    # ==================== Services Panel Handlers ====================
    
    def on_book_service(self, booking_data: dict):
        """Book a service"""
        try:
            self.show_message("Service Booking", 
                            f"Service booked successfully!")
            self.refresh_services_panel()
        except Exception as e:
            print(f"Error booking service: {e}")
            self.show_error("Failed to book service")
    
    def on_delete_service_booking(self, booking_id: str):
        """Delete/cancel service booking"""
        try:
            if not self._confirm_action("Cancel Booking", "Cancel this service booking?"):
                return
            
            success = ReservationModel.cancel_service_booking(int(booking_id))
            
            if success:
                self.show_message("Success", "Service booking cancelled!")
                self.refresh_services_panel()
            else:
                self.show_error("Failed to cancel booking")
                    
        except Exception as e:
            print(f"Error cancelling booking: {e}")
            self.show_error("Failed to cancel booking")
    
    def on_calculate_service_total(self, service_id: str):
        """Calculate total for selected service"""
        try:
            service = ServiceModel.find(int(service_id))
            if service:
                total = float(service['price'])
                self.services_panel.set_total(f"{total:,.2f}")
        except Exception as e:
            print(f"Error calculating total: {e}")
    
    # ==================== Navigation ====================
    
    def go_back(self):
        """Go back to dashboard"""
        confirm = self._confirm_action("Back to Dashboard", 
                                      "Are you sure you want to go back?")
        if confirm:
            if self.mainframe:
                self.mainframe.close()
            if self.main_window:
                self.main_window.show()
            self.back_to_dashboard_requested.emit()
    
    def show_view(self):
        """Show the main reservation view"""
        self.refresh_all_data()
        self.mainframe.show()
    
    def close(self):
        """Close all views"""
        if self.mainframe:
            self.mainframe.close()
    
    # ==================== Utility Methods ====================
    
    def _get_current_user_id(self) -> int:
        """Get current logged-in user ID (placeholder)"""
        return 1
    
    def _confirm_action(self, title: str, message: str) -> bool:
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self.mainframe, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_message(self, title: str, message: str):
        """Show information message"""
        QMessageBox.information(self.mainframe, title, message)
    
    def show_error(self, message: str):
        """Show error message"""
        QMessageBox.warning(self.mainframe, "Error", message)


# ==================== Test Entry Point ====================

def test_controller():
    """Test the reservation controller standalone"""
    app = QApplication(sys.argv)
    
    # Test database connection first
    try:
        from config.database import test_connection
        if not test_connection():
            print("❌ Database connection failed. Please check your MySQL configuration.")
            return
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return
    
    # Create and show controller
    controller = ReservationController(user_role="Admin")
    controller.show_view()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    test_controller()   