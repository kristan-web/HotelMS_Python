"""
Dashboard Controller
=====================
Provides statistics for admin and staff dashboards.
Connects to models to retrieve real-time data.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.reservation_model import ReservationModel
from models.service_model import ServiceModel
from models.user_model import UserModel
from models.receipt_model import ReceiptModel
from models.room_model import RoomModel
from datetime import date


class DashboardController:
    """Controller for dashboard statistics."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        pass
    
    # ── ADMIN DASHBOARD STATS ──────────────────────────────────────────────
    def get_admin_stats(self) -> dict:
        """
        Return statistics for admin dashboard.
        Returns dict with keys: total_reservations, available_services,
                                total_staff, total_revenue
        """
        # Total reservations (confirmed and checked-in)
        reservations = ReservationModel.get_all("ALL")
        total_reservations = len([r for r in reservations if r['status'] in ['CONFIRMED', 'CHECKED_IN']])
        
        # Available services (active and not deleted)
        available_services = len(ServiceModel.get_all_active())
        
        # Total staff (active staff accounts)
        all_users = UserModel.get_all_active()
        total_staff = len([u for u in all_users if u['role'] == 'Staff'])
        
        # Total revenue (sum of all receipt totals)
        total_revenue = self._get_total_revenue()
        
        return {
            'total_reservations': total_reservations,
            'available_services': available_services,
            'total_staff': total_staff,
            'total_revenue': total_revenue
        }
    
    def _get_total_revenue(self) -> float:
        """Calculate total revenue from all receipts."""
        try:
            from utils.db_connection import get_connection
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT SUM(total) as total_revenue FROM receipts")
            result = cursor.fetchone()
            cursor.close()
            return float(result['total_revenue']) if result['total_revenue'] else 0.0
        except Exception as e:
            print(f"[DashboardController] Error getting total revenue: {e}")
            return 0.0
    
    # ── STAFF DASHBOARD STATS ──────────────────────────────────────────────
    def get_staff_today_stats(self) -> dict:
        """
        Return today's statistics for staff dashboard.
        Returns dict with keys: todays_reservations, todays_checkins,
                                todays_checkouts, todays_revenue
        """
        today = date.today().isoformat()
        
        # Get all reservations
        all_reservations = ReservationModel.get_all("ALL")
        
        # Today's reservations (confirmed or checked-in for today)
        todays_reservations = len([
            r for r in all_reservations 
            if r['check_in'] == today and r['status'] in ['CONFIRMED', 'CHECKED_IN']
        ])
        
        # Today's check-ins
        todays_checkins = len([
            r for r in all_reservations 
            if r['check_in'] == today and r['status'] == 'CHECKED_IN'
        ])
        
        # Today's check-outs
        todays_checkouts = len([
            r for r in all_reservations 
            if r['check_out'] == today and r['status'] == 'CHECKED_OUT'
        ])
        
        # Today's revenue (sum of checked-out reservations for today)
        todays_revenue = sum([
            float(r.get('total_price', 0)) 
            for r in all_reservations 
            if r['check_out'] == today and r['status'] == 'CHECKED_OUT'
        ])
        
        return {
            'todays_reservations': todays_reservations,
            'todays_checkins': todays_checkins,
            'todays_checkouts': todays_checkouts,
            'todays_revenue': todays_revenue
        }
    
    # ── ROOM OCCUPANCY STATS ───────────────────────────────────────────────
    def get_room_occupancy(self) -> dict:
        """
        Return room occupancy statistics.
        Returns dict with keys: total_rooms, occupied_rooms, available_rooms, maintenance_rooms
        """
        rooms = RoomModel.get_all()
        
        total_rooms = len(rooms)
        occupied_rooms = len([r for r in rooms if r['status'] == 'OCCUPIED'])
        available_rooms = len([r for r in rooms if r['status'] == 'AVAILABLE'])
        maintenance_rooms = len([r for r in rooms if r['status'] == 'MAINTENANCE'])
        
        return {
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'maintenance_rooms': maintenance_rooms
        }
    
    # ── MONTHLY REVENUE (for reports) ──────────────────────────────────────
    def get_monthly_revenue(self, year: int = None, month: int = None) -> float:
        """
        Get revenue for a specific month.
        If year and month not provided, uses current month.
        """
        import datetime
        
        if year is None or month is None:
            now = datetime.datetime.now()
            year = now.year
            month = now.month
        
        start_date = f"{year}-{month:02d}-01"
        
        # Calculate end date
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        try:
            from utils.db_connection import get_connection
            conn = get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT SUM(total) as revenue
                FROM receipts
                WHERE issued_at >= %s AND issued_at < %s
            """, (start_date, end_date))
            result = cursor.fetchone()
            cursor.close()
            return float(result['revenue']) if result['revenue'] else 0.0
        except Exception as e:
            print(f"[DashboardController] Error getting monthly revenue: {e}")
            return 0.0


# ── Singleton instance ──────────────────────────────────────────────────────
_dashboard_controller = DashboardController()


def get_dashboard_controller():
    """Return the singleton dashboard controller instance."""
    return _dashboard_controller