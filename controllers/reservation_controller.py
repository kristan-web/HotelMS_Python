"""
Reservation Controller for Hotel Management System
Connects all reservation-related views with models
"""

import sys
import os
from typing import Optional, Dict, Any, List
from datetime import date, datetime

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
    
    def __init__(self, main_window=None, user_role: str = "Staff", user_id: int = None):
        super().__init__()
        self.main_window = main_window
        self.user_role = user_role
        self.user_id = user_id
        self.is_initialized = False
        
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
        self.is_initialized = True
        print("✅ Reservation controller initialized")
    
    def _init_views(self):
        """Initialize all views"""
        try:
            self.mainframe = MainFrameView(user_role=self.user_role, controller=self)
            self.reservation_panel = ReservationPanel()
            self.guest_panel = GuestPanelView()
            self.room_panel = RoomPanel()
            self.services_panel = ServicesPanel()
            print(f"✅ RoomPanel created in controller: {self.room_panel}")
            print(f"✅ RoomPanel instance id in controller: {id(self.room_panel)}")
        
            # Set parent
            if self.main_window:
                self.mainframe.setParent(self.main_window)
        
            # Add tabs
            self.mainframe.add_tab(self.reservation_panel, "RESERVATIONS")
            self.mainframe.add_tab(self.guest_panel, "GUESTS")
            self.mainframe.add_tab(self.room_panel, "ROOMS")
        
            # Add ServicesPanel only for Admin users
            print(f"🔍 user_role: {self.user_role}")
            if self.user_role == "Admin":
                self.mainframe.add_tab(self.services_panel, "SERVICES")
                print("✅ ServicesPanel added to mainframe")
            else:
                print(f"⚠️ ServicesPanel NOT added - user_role: {self.user_role}")
        
            print("✅ Reservation views initialized")
        except Exception as e:
            print(f"❌ Error initializing reservation views: {e}")
            import traceback    
            traceback.print_exc()
    
    def _connect_signals(self):
        """Connect view signals to controller methods"""
        try:
            # Mainframe signals
            if self.mainframe and hasattr(self.mainframe, 'back_btn'):
                self.mainframe.back_btn.clicked.connect(self.go_back)
            
            # ReservationPanel signals
            if self.reservation_panel:
                print("✅ Connecting ReservationPanel signals...")
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
            if self.guest_panel:
                print("✅ Connecting GuestPanel signals...")
                self.guest_panel.add_guest_requested.connect(self.on_add_guest)
                self.guest_panel.edit_guest_requested.connect(self.on_edit_guest)
                self.guest_panel.delete_guest_requested.connect(self.on_delete_guest)
                self.guest_panel.refresh_requested.connect(self.refresh_guests)
                self.guest_panel.clear_form_requested.connect(self.on_clear_guest_form)
            
            # RoomPanel signals
            # RoomPanel signals
            if self.room_panel:
                print("✅ Connecting RoomPanel signals...")
                print(f"   - room_panel instance id in controller: {id(self.room_panel)}")
                self.room_panel.add_room_requested.connect(self.on_add_room)
                self.room_panel.edit_room_requested.connect(self.on_edit_room)
                # REMOVED: self.room_panel.delete_room_requested.connect(self.on_delete_room)
                self.room_panel.update_status_requested.connect(self.on_update_room_status)
                print("   - update_status_requested connected")
                self.room_panel.refresh_requested.connect(self.refresh_rooms)
                self.room_panel.clear_form_requested.connect(self.on_clear_room_form)
            
            # ServicesPanel signals
            if self.services_panel:
                print(f"✅ Connecting ServicesPanel signals...")
                self.services_panel.book_service_requested.connect(self.on_book_service)
                self.services_panel.delete_booking_requested.connect(self.on_delete_service_booking)
                self.services_panel.refresh_requested.connect(self.refresh_services_panel)
                self.services_panel.calculate_total_requested.connect(self.on_calculate_service_total)
            else:
                print("❌ services_panel is None! Cannot connect signals.")
            
            print("✅ Reservation signals connected")
        except Exception as e:
            print(f"❌ Error connecting reservation signals: {e}")
            import traceback
            traceback.print_exc()
    
    # ==================== Data Loading Methods ====================
    
    def refresh_all_data(self):
        """Refresh all panels with latest data"""
        print("🔄 Refreshing all reservation data...")
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
            print(f"📊 Loaded {len(reservations)} reservations")
            if self.reservation_panel:
                self.reservation_panel.load_reservations(reservations)
        except Exception as e:
            print(f"❌ Error loading reservations: {e}")
            import traceback
            traceback.print_exc()
            if self.reservation_panel:
                self.reservation_panel.show_error("Failed to load reservations")
    
    def refresh_guests(self):
        """Refresh guest table"""
        try:
            guests = GuestModel.get_all_active()
            print(f"📊 Loaded {len(guests)} guests")
            if self.guest_panel:
                self.guest_panel.load_table(guests)
        except Exception as e:
            print(f"❌ Error loading guests: {e}")
            import traceback
            traceback.print_exc()
            if self.guest_panel:
                self.guest_panel.show_error("Failed to load guests")
    
    def refresh_rooms(self):
        """Refresh room table"""
        try:
            rooms = RoomModel.get_all_active()
            print(f"📊 Loaded {len(rooms)} rooms")
            if self.room_panel:
                self.room_panel.load_rooms(rooms)
        except Exception as e:
            print(f"❌ Error loading rooms: {e}")
            import traceback
            traceback.print_exc()
            if self.room_panel:
                self.room_panel.show_error("Failed to load rooms")
    
    def refresh_services_panel(self):
        """Refresh services panel data"""
        try:
            print("🔄 Refreshing services panel...")
            # Load guests for combo
            guests = GuestModel.get_all_active()
            if self.services_panel:
                formatted_guests = []
                for g in guests:
                    formatted_guests.append({
                        'id': g.get('id', g.get('guest_id')),
                        'first_name': g.get('first_name', ''),
                        'last_name': g.get('last_name', '')
                    })
                self.services_panel.load_guests(formatted_guests)
                print(f"📊 Loaded {len(formatted_guests)} guests for services panel")
            
            # Load services for combo
            services = ServiceModel.get_all_active()
            if self.services_panel:
                formatted_services = []
                for s in services:
                    formatted_services.append({
                        'id': s.get('id', s.get('service_id')),
                        'name': s.get('name', ''),
                        'price': s.get('price', 0)
                    })
                self.services_panel.load_services(formatted_services)
                print(f"📊 Loaded {len(formatted_services)} services for services panel")
            
            # Load bookings (reservation_services)
            bookings = self._get_all_service_bookings()
            if self.services_panel:
                self.services_panel.load_bookings(bookings)
                print(f"📊 Loaded {len(bookings)} service bookings")
            
        except Exception as e:
            print(f"❌ Error loading services panel: {e}")
            import traceback
            traceback.print_exc()
    
    def load_guest_combo(self):
        """Load guests into reservation panel combo box"""
        try:
            guests = GuestModel.get_all_for_combo()
            if self.reservation_panel:
                self.reservation_panel.load_guests(guests)
                print(f"📊 Loaded {len(guests)} guests into combo")
        except Exception as e:
            print(f"❌ Error loading guest combo: {e}")
    
    def load_room_combo(self, rooms: list):
        """Load available rooms into reservation panel combo box"""
        if self.reservation_panel:
            self.reservation_panel.load_rooms(rooms)
    
    def load_service_combo(self):
        """Load services into services panel combo box"""
        try:
            services = ServiceModel.get_all_active()
            if self.services_panel:
                formatted_services = []
                for s in services:
                    formatted_services.append({
                        'id': s.get('id', s.get('service_id')),
                        'name': s.get('name', ''),
                        'price': s.get('price', 0)
                    })
                self.services_panel.load_services(formatted_services)
        except Exception as e:
            print(f"❌ Error loading service combo: {e}")
    
    def _get_all_service_bookings(self) -> List[Dict]:
        """Get all service bookings from reservation_services"""
        try:
            # Check if table exists first
            check_table = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'hotel_ms' 
                AND table_name = 'reservation_services'
            """
            from config.database import DatabaseQuery
            table_exists = DatabaseQuery.fetch_one(check_table)
            
            if not table_exists or table_exists.get('count', 0) == 0:
                # Table doesn't exist yet, return empty list
                return []
            
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
            return DatabaseQuery.fetch_all(query)
        except Exception as e:
            print(f"❌ Error getting service bookings: {e}")
            return []
    
    # ==================== Reservation Panel Handlers ====================
    
    def on_find_rooms(self, check_in: str, check_out: str):
        """Find available rooms for selected dates"""
        try:
            rooms = RoomModel.get_available_rooms(check_in, check_out)
            
            print(f"🔍 Found {len(rooms)} available rooms for {check_in} to {check_out}")
            
            formatted_rooms = []
            for r in rooms:
                formatted_rooms.append({
                    'id': r.get('id'),
                    'room_number': r.get('room_number'),
                    'room_type': r.get('room_type'),
                    'price': r.get('price')
                })
            
            self.load_room_combo(formatted_rooms)
            
            if not rooms and self.reservation_panel:
                self.reservation_panel.show_message("No Rooms Available", 
                                "No rooms available for the selected dates.")
        except Exception as e:
            print(f"❌ Error finding rooms: {e}")
            import traceback
            traceback.print_exc()
            if self.reservation_panel:
                self.reservation_panel.show_error(f"Failed to find available rooms: {str(e)}")
    
    def on_confirm_reservation(self, reservation_data: dict):
        """Confirm and create reservation"""
        try:
            user_id = self.user_id if self.user_id else 1
            
            guest_id = reservation_data.get('guest_id')
            room_id = reservation_data.get('room_id')
            check_in = reservation_data.get('check_in')
            check_out = reservation_data.get('check_out')
            notes = reservation_data.get('notes', '')
            
            if not guest_id:
                self.show_error("Please select a guest.")
                return
            if not room_id:
                self.show_error("Please select a room.")
                return
            if not check_in or not check_out:
                self.show_error("Please select check-in and check-out dates.")
                return
            
            data = {
                'guest_id': guest_id,
                'room_id': room_id,
                'check_in': check_in,
                'check_out': check_out,
                'notes': notes,
                'services': []
            }
            
            reservation_id = ReservationModel.create_reservation(data, user_id)
            
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
            print(f"❌ Error confirming reservation: {e}")
            import traceback
            traceback.print_exc()
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
            print(f"❌ Error checking in: {e}")
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
            print(f"❌ Error checking out: {e}")
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
            print(f"❌ Error cancelling: {e}")
            self.show_error("Failed to cancel reservation")
    
    def on_filter_reservations(self, status: str):
        """Filter reservations by status"""
        self.current_reservation_filter = status
        self.refresh_reservations()
        
    def on_room_selected(self, room_id: str):
        """Calculate total when room is selected"""
        try:
            if not self.reservation_panel:
                return
                
            check_in = self.reservation_panel.check_in_date
            check_out = self.reservation_panel.check_out_date
            
            if not check_in or not check_out:
                room = RoomModel.find(int(room_id))
                if room:
                    total = float(room['price'])
                    self.reservation_panel.set_total(f"{total:,.2f}")
            else:
                nights = (check_out - check_in).days
                if nights > 0:
                    room = RoomModel.find(int(room_id))
                    if room:
                        total = float(room['price']) * nights
                        self.reservation_panel.set_total(f"{total:,.2f}")
        except Exception as e:
            print(f"❌ Error calculating total: {e}")

    def on_dates_changed(self):
        """Update total when dates change"""
        if self.reservation_panel and self.reservation_panel.room_combo.currentData():
            self.on_room_selected(str(self.reservation_panel.room_combo.currentData()))
    
    def clear_reservation_form(self):
        """Clear reservation form fields"""
        if self.reservation_panel:
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
            if not all([guest_data.get('first_name'), guest_data.get('last_name'), 
                       guest_data.get('email'), guest_data.get('phone'), guest_data.get('address')]):
                self.show_error("All fields are required")
                return
            
            guest_id = GuestModel.create_guest(guest_data)
            
            if guest_id:
                self.show_message("Success", f"Guest '{guest_data['first_name']} {guest_data['last_name']}' added successfully!")
                if self.guest_panel:
                    self.guest_panel.clear_form()
                self.refresh_guests()
                self.load_guest_combo()
                self.refresh_services_panel()
            else:
                self.show_error("Failed to add guest")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"❌ Error adding guest: {e}")
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
                if self.guest_panel:
                    self.guest_panel.clear_form()
                self.refresh_guests()
                self.load_guest_combo()
                self.refresh_services_panel()
            else:
                self.show_error("Failed to update guest")
                
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"❌ Error editing guest: {e}")
            self.show_error("Failed to update guest")
    
    def on_delete_guest(self, guest_id: str):
        """Delete selected guest"""
        try:
            success = GuestModel.delete_guest(int(guest_id))
            
            if success:
                self.show_message("Success", "Guest deleted successfully!")
                self.refresh_guests()
                self.load_guest_combo()
                self.refresh_services_panel()
            else:
                self.show_error("Failed to delete guest")
                    
        except ValueError as e:
            self.show_error(str(e))
        except Exception as e:
            print(f"❌ Error deleting guest: {e}")
            self.show_error("Failed to delete guest")
    
    def on_clear_guest_form(self):
        """Clear guest form"""
        if self.guest_panel:
            self.guest_panel.clear_form()
    
    # ==================== Room Panel Handlers ====================
    
    def on_add_room(self, room_data: dict):
        """Add new room"""
        print(f"🔴🔴🔴 CONTROLLER RECEIVED add_room: {room_data}")
        try:
            room_id = RoomModel.create_room(room_data)
            
            if room_id:
                self.show_message("Success", f"Room '{room_data['room_number']}' added successfully!")
                self.refresh_rooms()
            else:
                self.show_error("Failed to add room")
                
        except ValueError as e:
            print(f"❌ ValueError: {e}")
            self.show_error(str(e))
        except Exception as e:
            print(f"❌ Error adding room: {e}")
            import traceback
            traceback.print_exc()
            self.show_error("Failed to add room")
    
    def on_edit_room(self, room_data: dict):
        """Edit existing room"""
        print(f"🔴🔴🔴 CONTROLLER RECEIVED edit_room: {room_data}")
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
            print(f"❌ ValueError: {e}")
            self.show_error(str(e))
        except Exception as e:
            print(f"❌ Error editing room: {e}")
            import traceback
            traceback.print_exc()
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
            print(f"❌ Error deleting room: {e}")
            self.show_error("Failed to delete room")
    
    def on_update_room_status(self, room_id: str, new_status: str):
        """Update room status using the RoomModel"""
        print(f"🔴🔴🔴 CONTROLLER RECEIVED update_status: room_id={room_id}, new_status={new_status}")
        try:
        # 1. Use the Model's update method
        # We pass a dictionary of just the fields we want to change
            success = RoomModel.update_room(int(room_id), {'status': new_status})
        
            if success:
                print(f"✅ SUCCESS: Room {room_id} is now {new_status}")
                self.show_message("Success", f"Room status updated to '{new_status}'!")
                self.refresh_rooms()
            else:
                print(f"⚠️ FAIL: RoomModel.update_room returned False for ID {room_id}")
                self.show_error("Failed to update room status")
            
        except Exception as e:
            print(f"❌ Error updating status: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"Failed to update status: {str(e)}")
    
    def on_clear_room_form(self):
        """Clear room form"""
        print("🧹 CONTROLLER RECEIVED clear_form")
        if self.room_panel:
            self.room_panel._clear_form_fields()
    
    # ==================== Services Panel Handlers ====================
    
    def on_book_service(self, booking_data: dict):
        """Book a service - create reservation service entry"""
        print(f"🔴🔴🔴 RESERVATION CONTROLLER RECEIVED BOOKING: {booking_data}")
        try:
            print(f"📝 Received booking data in controller: {booking_data}")
            
            # Validate required fields
            if not booking_data.get('guest_id'):
                self.show_error("Please select a guest.")
                return
            if not booking_data.get('service_id'):
                self.show_error("Please select a service.")
                return
            
            guest_id = booking_data['guest_id']
            
            # FIRST: Check all reservations for this guest (including cancelled/checked out)
            from config.database import DatabaseQuery
            
            all_reservations_query = """
                SELECT reservation_id, status, check_in, check_out
                FROM reservations 
                WHERE guest_id = %s
                ORDER BY created_at DESC
            """
            all_reservations = DatabaseQuery.fetch_all(all_reservations_query, (guest_id,))
            print(f"🔍 ALL reservations for guest {guest_id}: {all_reservations}")
            
            # Find active reservation for this guest (not checked out or cancelled)
            active_query = """
                SELECT reservation_id, status
                FROM reservations 
                WHERE guest_id = %s 
                AND status NOT IN ('CHECKED_OUT', 'CANCELLED')
                ORDER BY created_at DESC
                LIMIT 1
            """
            result = DatabaseQuery.fetch_one(active_query, (guest_id,))
            
            print(f"🔍 Active reservation for guest {guest_id}: {result}")
            
            if not result:
                self.show_error(f"No active reservation found for this guest. Please create a reservation first in the Reservations tab.\n\nGuest has {len(all_reservations)} total reservation(s) but none are active.")
                return
            
            reservation_id = result['reservation_id']
            service_id = booking_data['service_id']
            duration = booking_data.get('duration', 60)
            scheduled_time = booking_data.get('scheduled_time')
            total = booking_data.get('total', 0)
            unit_price = booking_data.get('unit_price', 0)
            
            # Get service details if unit_price not provided
            if unit_price == 0:
                service = ServiceModel.find(int(service_id))
                if not service:
                    self.show_error("Service not found.")
                    return
                unit_price = float(service['price'])
            
            # If total is 0, calculate it
            if total == 0:
                total = unit_price
            
            # Format scheduled_time properly with seconds
            try:
                if scheduled_time:
                    if len(scheduled_time) == 16:  # YYYY-MM-DD HH:MM
                        scheduled_time = f"{scheduled_time}:00"
                    elif len(scheduled_time) == 10:  # YYYY-MM-DD
                        scheduled_time = f"{scheduled_time} 00:00:00"
                else:
                    scheduled_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            except:
                scheduled_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"📝 Inserting with: reservation_id={reservation_id}, service_id={service_id}, unit_price={unit_price}, total={total}, scheduled_time={scheduled_time}, duration={duration}")
            
            # Check if reservation_services table exists
            check_table = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = 'hotel_ms' 
                AND table_name = 'reservation_services'
            """
            table_exists = DatabaseQuery.fetch_one(check_table)
            print(f"🔍 reservation_services table exists: {table_exists}")
            
            if not table_exists or table_exists.get('count', 0) == 0:
                # Table doesn't exist, let's create it
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS reservation_services (
                        res_service_id INT PRIMARY KEY AUTO_INCREMENT,
                        reservation_id INT NOT NULL,
                        service_id INT NOT NULL,
                        quantity INT DEFAULT 1,
                        unit_price DECIMAL(10,2) NOT NULL,
                        total DECIMAL(10,2) NOT NULL,
                        scheduled_at DATETIME,
                        duration INT,
                        status VARCHAR(20) DEFAULT 'PENDING',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        FOREIGN KEY (reservation_id) REFERENCES reservations(reservation_id) ON DELETE CASCADE,
                        FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
                    )
                """
                from config.database import execute_query
                execute_query(create_table_sql)
                print("✅ Created reservation_services table")
            
            # Now try to insert
            insert_sql = """
                INSERT INTO reservation_services 
                (reservation_id, service_id, quantity, unit_price, total, scheduled_at, duration, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING')
            """
            booking_id = DatabaseQuery.insert_and_get_id(
                insert_sql,
                (reservation_id, service_id, 1, unit_price, float(total), scheduled_time, duration)
            )
            
            print(f"📝 Insert result: booking_id={booking_id}")
            
            if booking_id:
                # Update reservation total
                update_total_query = """
                    UPDATE reservations 
                    SET total_price = (
                        SELECT COALESCE(SUM(total), 0) 
                        FROM reservation_services 
                        WHERE reservation_id = %s AND status != 'CANCELLED'
                    ) + (
                        SELECT (DATEDIFF(check_out, check_in) * rm.price)
                        FROM rooms rm 
                        WHERE rm.room_id = reservations.room_id
                    )
                    WHERE reservation_id = %s
                """
                DatabaseQuery.execute_query(update_total_query, (reservation_id, reservation_id))
                
                self.show_message("Success", "Service booked successfully!")
                self.refresh_services_panel()
                print(f"✅ Service booking created with ID: {booking_id}")
            else:
                self.show_error("Failed to book service - database insert failed")
                print("❌ Failed to insert service booking - insert returned None")
            
        except Exception as e:
            print(f"❌ Error booking service: {e}")
            import traceback
            traceback.print_exc()
            self.show_error(f"Failed to book service: {str(e)}")
    
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
            print(f"❌ Error cancelling booking: {e}")
            self.show_error("Failed to cancel booking")
    
    def on_calculate_service_total(self, service_id: str):
        """Calculate total for selected service based on duration"""
        try:
            service = ServiceModel.find(int(service_id))
            if service and self.services_panel:
                # Get duration from the panel
                duration_text = self.services_panel.txt_duration.text()
                if duration_text and duration_text.isdigit():
                    duration = int(duration_text)
                    unit_price = float(service['price'])
                    total = unit_price
                    self.services_panel.set_total(f"{total:,.2f}")
                else:
                    self.services_panel.set_total(f"{float(service['price']):,.2f}")
        except Exception as e:
            print(f"❌ Error calculating total: {e}")
    
    # ==================== Navigation ====================
    
    def go_back(self):
        """Go back to dashboard"""
        confirm = self._confirm_action("Back to Dashboard", 
                                      "Are you sure you want to go back?")
        if confirm:
            self.back_to_dashboard_requested.emit()
            print("🔙 Returning to dashboard")
    
    def show_view(self):
        """Show the main reservation view"""
        print("🖥️ Showing reservation view")
        self.refresh_all_data()
        if self.mainframe:
            self.mainframe.show()
    
    def close(self):
        """Close all views and clean up"""
        print("🔒 Closing reservation controller")
        if self.mainframe:
            self.mainframe.close()
    
    # ==================== Utility Methods ====================
    
    def _get_current_user_id(self) -> int:
        """Get current logged-in user ID"""
        return self.user_id if self.user_id else 1
    
    def _confirm_action(self, title: str, message: str) -> bool:
        """Show confirmation dialog"""
        if not self.mainframe:
            return False
            
        reply = QMessageBox.question(
            self.mainframe, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_message(self, title: str, message: str):
        """Show information message"""
        if self.mainframe:
            QMessageBox.information(self.mainframe, title, message)
    
    def show_error(self, message: str):
        """Show error message"""
        if self.mainframe:
            QMessageBox.warning(self.mainframe, "Error", message)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    controller = ReservationController(user_role="Admin")
    controller.show_view()
    sys.exit(app.exec())