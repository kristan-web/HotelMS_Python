"""
Receipt Controller
===================
Manages receipt operations, connects ReceiptModel with views.
Handles receipt generation and formatting.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.receipt_model import ReceiptModel
from models.reservation_model import ReservationModel


class ReceiptController:
    """Controller for receipt management operations."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── GET METHODS ────────────────────────────────────────────────────────
    def get_by_reservation(self, reservation_id: int) -> dict | None:
        """
        Get receipt data for a reservation.
        Returns formatted receipt data for display.
        """
        receipt = ReceiptModel.get_by_reservation(reservation_id)
        
        if not receipt:
            return None
        
        # Format receipt data
        return {
            'receipt_id': receipt['receipt_id'],
            'receipt_number': receipt['receipt_number'],
            'subtotal': float(receipt['subtotal']),
            'tax': float(receipt['tax']),
            'total': float(receipt['total']),
            'issued_at': receipt['issued_at'],
            'guest_name': receipt['guest_name'],
            'guest_address': receipt['guest_address'],
            'room_number': receipt['room_number'],
            'room_type': receipt['room_type'],
            'check_in': receipt['check_in'],
            'check_out': receipt['check_out'],
            'nights': receipt['nights'],
            'room_total': float(receipt['total_price'])
        }
    
    def get_by_id(self, receipt_id: int) -> dict | None:
        """Get receipt by ID."""
        receipt = ReceiptModel.get_by_id(receipt_id)
        
        if not receipt:
            return None
        
        return {
            'receipt_id': receipt['receipt_id'],
            'reservation_id': receipt['reservation_id'],
            'receipt_number': receipt['receipt_number'],
            'subtotal': float(receipt['subtotal']),
            'tax': float(receipt['tax']),
            'total': float(receipt['total']),
            'issued_at': receipt['issued_at']
        }
    
    # ── RECEIPT GENERATION ─────────────────────────────────────────────────
    def generate_receipt_data(self, reservation_id: int) -> dict | None:
        """
        Generate receipt data for display.
        This can be used before actually saving to database.
        """
        reservation = ReservationModel.get_by_id(reservation_id)
        if not reservation:
            return None
        
        # Get services
        services = ReservationModel.get_services(reservation_id)
        
        # Calculate totals
        subtotal = float(reservation.get('total_price', 0))
        tax = subtotal * 0.12  # 12% VAT
        total = subtotal + tax
        
        # Format receipt data
        return {
            'reservation_id': reservation_id,
            'guest_name': f"{reservation.get('guest_name', '')}",
            'guest_address': '',  # Would need to fetch from guest model
            'room_number': reservation.get('room_number', ''),
            'room_type': reservation.get('room_type', ''),
            'check_in': str(reservation.get('check_in', '')),
            'check_out': str(reservation.get('check_out', '')),
            'nights': reservation.get('nights', 0),
            'services': [
                {
                    'name': s.get('service_name', ''),
                    'quantity': s.get('quantity', 1),
                    'unit_price': float(s.get('unit_price', 0)),
                    'total': float(s.get('total', 0))
                }
                for s in services
            ],
            'subtotal': subtotal,
            'tax': tax,
            'total': total
        }


# ── Singleton instance ──────────────────────────────────────────────────────
_receipt_controller = ReceiptController()


def get_receipt_controller():
    """Return the singleton receipt controller instance."""
    return _receipt_controller