"""
Reservation Controller
=======================
Manages reservation operations, connects ReservationModel with views.
Handles validation, price calculation, and receipt generation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.reservation_model import ReservationModel
from models.room_model import RoomModel
from models.receipt_model import ReceiptModel
from models.admin_log_model import AdminLogModel
from controllers.auth_controller import get_auth_controller
from datetime import datetime, date
import json


class ReservationController:
    """Controller for reservation management operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── DATA TRANSFORMATION ────────────────────────────────────────────────
    def _transform_reservation(self, res: dict) -> dict:
        """Transform reservation data for view compatibility."""
        if not res:
            return None
        return {
            'id': res['reservation_id'],
            'guest_id': res.get('guest_id'),
            'guest_name': res.get('guest_name', ''),
            'room_id': res.get('room_id'),
            'room_number': res.get('room_number', ''),
            'room_type': res.get('room_type', ''),
            'check_in': res['check_in'],
            'check_out': res['check_out'],
            'nights': res.get('nights', 0),
            'total_price': float(res.get('total_price', 0)),
            'notes': res.get('notes', ''),
            'status': res['status'],
            'created_at': res.get('created_at', '')
        }
    
    def _transform_reservations_list(self, reservations: list) -> list:
        """Transform list of reservations."""
        return [self._transform_reservation(r) for r in reservations]
    
    # ── PRICE CALCULATION ──────────────────────────────────────────────────
    def _calculate_total_price(self, room_id: int, check_in: str, 
                                check_out: str, services: list = None) -> float:
        """
        Calculate total price for a reservation.
        Room price × nights + service charges.
        """
        room = RoomModel.get_by_id(room_id)
        if not room:
            return 0.0
        
        # Calculate nights
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
        nights = (check_out_date - check_in_date).days
        
        # Room total
        room_total = float(room['price']) * nights
        
        # Service total
        service_total = 0.0
        if services:
            for svc in services:
                service_total += float(svc.get('total', 0))
        
        return room_total + service_total
    
    # ── VALIDATION ─────────────────────────────────────────────────────────
    def _validate_dates(self, check_in: str, check_out: str) -> tuple:
        """Validate date range. Returns (is_valid, error_message)."""
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            if check_in_date >= check_out_date:
                return (False, "Check-out date must be after check-in date.")
            
            if check_in_date < date.today():
                return (False, "Check-in date cannot be in the past.")
            
            return (True, "")
        except ValueError:
            return (False, "Invalid date format. Use YYYY-MM-DD.")
    
    # ── CRUD OPERATIONS ────────────────────────────────────────────────────
    def create(self, guest_id: int, room_id: int, user_id: int,
               check_in: str, check_out: str, notes: str = "") -> tuple:
        """
        Create a new reservation.
        Returns (success, message, reservation_id)
        """
        # Validate dates
        is_valid, error_msg = self._validate_dates(check_in, check_out)
        if not is_valid:
            return (False, error_msg, None)
        
        # Calculate total price
        total_price = self._calculate_total_price(room_id, check_in, check_out)
        
        # Create reservation
        reservation_id = ReservationModel.create(
            guest_id, room_id, user_id, check_in, check_out, total_price, notes
        )
        
        if reservation_id:
            # Update room status to OCCUPIED
            RoomModel.update_status(room_id, 'OCCUPIED')
            
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="CREATE_RESERVATION",
                    description=f"Created reservation ID {reservation_id} for guest ID {guest_id}"
                )
            return (True, "Reservation created successfully!", reservation_id)
        else:
            return (False, "Failed to create reservation. Please try again.", None)
    
    def get_all(self, status_filter: str = "ALL") -> list:
        """Return all reservations, optionally filtered by status."""
        reservations = ReservationModel.get_all(status_filter)
        return self._transform_reservations_list(reservations)
    
    def get_by_id(self, reservation_id: int) -> dict | None:
        """Return a single reservation by ID."""
        reservation = ReservationModel.get_by_id(reservation_id)
        return self._transform_reservation(reservation)
    
    def get_today_stats(self) -> dict:
        """Return today's reservation statistics for staff dashboard."""
        return ReservationModel.get_today_stats()
    
    def update_status(self, reservation_id: int, new_status: str) -> tuple:
        """
        Update reservation status (check-in, check-out, cancel).
        Returns (success, message)
        """
        valid_statuses = ['CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED']
        if new_status not in valid_statuses:
            return (False, f"Invalid status. Must be one of: {valid_statuses}")
        
        # Get current reservation
        reservation = ReservationModel.get_by_id(reservation_id)
        if not reservation:
            return (False, "Reservation not found.")
        
        old_status = reservation['status']
        
        # Handle status-specific actions
        if new_status == 'CHECKED_IN' and old_status != 'CONFIRMED':
            return (False, "Only CONFIRMED reservations can be checked in.")
        
        if new_status == 'CHECKED_OUT':
            if old_status != 'CHECKED_IN':
                return (False, "Only CHECKED_IN reservations can be checked out.")
            # Generate receipt on check-out
            receipt = self._generate_receipt(reservation_id)
            if not receipt:
                return (False, "Failed to generate receipt.")
        
        if new_status == 'CANCELLED' and old_status in ['CHECKED_OUT', 'CANCELLED']:
            return (False, f"Cannot cancel a reservation that is already {old_status}.")
        
        # Update status
        success = ReservationModel.update_status(reservation_id, new_status)
        
        if success:
            # Update room status if checking in or cancelling
            if new_status == 'CHECKED_IN':
                RoomModel.update_status(reservation['room_id'], 'OCCUPIED')
            elif new_status == 'CANCELLED' and old_status == 'CONFIRMED':
                RoomModel.update_status(reservation['room_id'], 'AVAILABLE')
            elif new_status == 'CHECKED_OUT':
                RoomModel.update_status(reservation['room_id'], 'AVAILABLE')
            
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="UPDATE_RESERVATION_STATUS",
                    description=f"Reservation {reservation_id} status changed from {old_status} to {new_status}"
                )
            return (True, f"Reservation status updated to {new_status}.")
        else:
            return (False, "Failed to update reservation status.")
    
    def _generate_receipt(self, reservation_id: int) -> str | None:
        """
        Generate receipt for a reservation.
        Returns receipt_number or None on failure.
        """
        reservation = ReservationModel.get_by_id(reservation_id)
        if not reservation:
            return None
        
        # Get services total
        services = ReservationModel.get_services(reservation_id)
        service_total = sum(float(s.get('total', 0)) for s in services)
        
        # Calculate totals
        subtotal = float(reservation.get('total_price', 0))
        tax = subtotal * 0.12  # 12% VAT
        total = subtotal + tax
        
        # Create receipt
        receipt_number = ReceiptModel.create(reservation_id, subtotal, tax, total)
        
        return receipt_number
    
    def add_service(self, reservation_id: int, service_id: int,
                    quantity: int, unit_price: float,
                    discount: float = 0.0, tax: float = 0.0,
                    scheduled_at: str = None, duration: int = 0) -> tuple:
        """
        Add a service to a reservation.
        Returns (success, message)
        """
        success = ReservationModel.add_service(
            reservation_id, service_id, quantity, unit_price,
            discount, tax, scheduled_at, duration
        )
        
        if success:
            # Recalculate total price
            reservation = ReservationModel.get_by_id(reservation_id)
            if reservation:
                new_total = self._calculate_total_price(
                    reservation['room_id'],
                    str(reservation['check_in']),
                    str(reservation['check_out'])
                )
                # Update reservation total
                import mysql.connector
                from utils.db_connection import get_connection
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE reservations SET total_price = %s WHERE reservation_id = %s",
                    (new_total, reservation_id)
                )
                conn.commit()
                cursor.close()
            
            # Log the action
            user = get_auth_controller().get_current_user()
            if user:
                AdminLogModel.log(
                    user_id=user['user_id'],
                    action="ADD_RESERVATION_SERVICE",
                    description=f"Added service ID {service_id} to reservation {reservation_id}"
                )
            return (True, "Service added successfully!")
        else:
            return (False, "Failed to add service.")
    
    def get_services(self, reservation_id: int) -> list:
        """Return all services for a reservation."""
        return ReservationModel.get_services(reservation_id)


# ── Singleton instance ──────────────────────────────────────────────────────
_reservation_controller = ReservationController()


def get_reservation_controller():
    """Return the singleton reservation controller instance."""
    return _reservation_controller