"""
Reservation Model for Hotel Management System
Handles CRUD operations for reservations with services integration
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date
from models.base_model import BaseModel
from config.database import DatabaseQuery


class ReservationModel(BaseModel):
    """
    Model for reservation operations
    Table: reservations
    """
    
    table_name = 'reservations'
    primary_key = 'reservation_id'
    
    # Columns that should be excluded from automatic updates
    exclude_from_update = ['reservation_id', 'created_at', 'nights']
    
    # Status choices
    STATUS_CHOICES = ['CONFIRMED', 'CHECKED_IN', 'CHECKED_OUT', 'CANCELLED']
    
    @classmethod
    def get_all_active(cls, status_filter: str = None) -> List[Dict[str, Any]]:
        """Get all reservations with optional status filter"""
        if status_filter and status_filter != "ALL":
            query = """
                SELECT 
                    r.reservation_id as id,
                    CONCAT(g.first_name, ' ', g.last_name) as guest_name,
                    rm.room_number,
                    r.check_in,
                    r.check_out,
                    r.nights,
                    r.total_price as total,
                    r.status,
                    r.notes,
                    r.created_at
                FROM reservations r
                JOIN guests g ON r.guest_id = g.guest_id
                JOIN rooms rm ON r.room_id = rm.room_id
                WHERE r.status = %s AND r.is_deleted = FALSE
                ORDER BY r.created_at DESC
            """
            return DatabaseQuery.fetch_all(query, (status_filter,))
        
        query = """
            SELECT 
                r.reservation_id as id,
                CONCAT(g.first_name, ' ', g.last_name) as guest_name,
                rm.room_number,
                r.check_in,
                r.check_out,
                r.nights,
                r.total_price as total,
                r.status,
                r.notes,
                r.created_at
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.is_deleted = FALSE
            ORDER BY r.created_at DESC
        """
        return DatabaseQuery.fetch_all(query)
    
    @classmethod
    def get_by_id(cls, reservation_id: int) -> Optional[Dict[str, Any]]:
        """Get reservation by ID with details"""
        query = """
            SELECT 
                r.reservation_id as id,
                r.guest_id,
                CONCAT(g.first_name, ' ', g.last_name) as guest_name,
                g.first_name,
                g.last_name,
                g.email,
                g.phone,
                r.room_id,
                rm.room_number,
                rm.room_type,
                rm.price as room_price,
                r.check_in,
                r.check_out,
                r.nights,
                r.total_price as total,
                r.status,
                r.notes,
                r.created_at,
                r.updated_at
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.reservation_id = %s
        """
        return DatabaseQuery.fetch_one(query, (reservation_id,))
    
    @classmethod
    def get_by_guest_id(cls, guest_id: int) -> List[Dict[str, Any]]:
        """Get all reservations for a specific guest"""
        query = """
            SELECT 
                r.reservation_id as id,
                rm.room_number,
                r.check_in,
                r.check_out,
                r.nights,
                r.total_price as total,
                r.status
            FROM reservations r
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.guest_id = %s
            ORDER BY r.created_at DESC
        """
        return DatabaseQuery.fetch_all(query, (guest_id,))
    
    @classmethod
    def get_by_date_range(cls, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get reservations within date range"""
        query = """
            SELECT 
                r.reservation_id as id,
                CONCAT(g.first_name, ' ', g.last_name) as guest_name,
                rm.room_number,
                r.check_in,
                r.check_out,
                r.nights,
                r.total_price as total,
                r.status
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.check_in <= %s AND r.check_out >= %s
            ORDER BY r.check_in
        """
        return DatabaseQuery.fetch_all(query, (end_date, start_date))
    
    @classmethod
    def get_total_revenue(cls) -> float:
        """Get total revenue from all completed reservations"""
        query = """
            SELECT COALESCE(SUM(total_price), 0) as total
            FROM reservations
            WHERE status = 'CHECKED_OUT'
        """
        result = DatabaseQuery.fetch_one(query)
        return float(result['total']) if result else 0.0
    
    @classmethod
    def get_today_revenue(cls) -> float:
        """Get revenue from today's completed reservations"""
        today = date.today().strftime('%Y-%m-%d')
        query = """
            SELECT COALESCE(SUM(total_price), 0) as total
            FROM reservations
            WHERE status = 'CHECKED_OUT'
            AND DATE(updated_at) = %s
        """
        result = DatabaseQuery.fetch_one(query, (today,))
        return float(result['total']) if result else 0.0
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """Get reservation statistics"""
        query = """
            SELECT 
                COUNT(*) as total_reservations,
                SUM(CASE WHEN status = 'CONFIRMED' THEN 1 ELSE 0 END) as confirmed,
                SUM(CASE WHEN status = 'CHECKED_IN' THEN 1 ELSE 0 END) as checked_in,
                SUM(CASE WHEN status = 'CHECKED_OUT' THEN 1 ELSE 0 END) as checked_out,
                SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) as cancelled,
                COALESCE(SUM(CASE WHEN status = 'CHECKED_OUT' THEN total_price ELSE 0 END), 0) as total_revenue
            FROM reservations
            WHERE is_deleted = FALSE
        """
        result = DatabaseQuery.fetch_one(query)
        return result or {}
    
    @classmethod
    def create_reservation(cls, data: Dict[str, Any], user_id: int) -> Optional[int]:
        """
        Create a new reservation
        data: guest_id, room_id, check_in, check_out, notes, total_price
        user_id: staff/admin who created the reservation
        """
        required = ['guest_id', 'room_id', 'check_in', 'check_out']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f"{field} is required")
        
        # Validate dates
        check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
        check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
        
        if check_in >= check_out:
            raise ValueError("Check-out date must be after check-in date")
        
        if check_in < date.today():
            raise ValueError("Check-in date cannot be in the past")
        
        # Check room availability
        if not cls.is_room_available(data['room_id'], data['check_in'], data['check_out']):
            raise ValueError("Room is not available for the selected dates")
        
        # Calculate nights and total
        nights = (check_out - check_in).days
        total_price = cls.calculate_total(data['room_id'], nights, data.get('services', []))
        
        # Prepare data for insert
        insert_data = {
            'guest_id': data['guest_id'],
            'room_id': data['room_id'],
            'user_id': user_id,
            'check_in': data['check_in'],
            'check_out': data['check_out'],
            'total_price': total_price,
            'notes': data.get('notes', ''),
            'status': 'CONFIRMED',
            'is_deleted': 0
        }
        
        reservation_id = cls.create(insert_data)
        
        # Add services if any
        if reservation_id and data.get('services'):
            cls.add_services_to_reservation(reservation_id, data['services'])
            # Recalculate total with services
            cls.update_reservation_total(reservation_id)
        
        return reservation_id
    
    @classmethod
    def update_reservation(cls, reservation_id: int, data: Dict[str, Any]) -> bool:
        """Update an existing reservation"""
        existing = cls.find(reservation_id)
        if not existing:
            raise ValueError(f"Reservation with ID {reservation_id} not found")
        
        # Prevent update if already checked out or cancelled
        if existing['status'] in ['CHECKED_OUT', 'CANCELLED']:
            raise ValueError(f"Cannot update {existing['status']} reservation")
        
        # Validate dates if changed
        if 'check_in' in data and 'check_out' in data:
            check_in = datetime.strptime(data['check_in'], '%Y-%m-%d').date()
            check_out = datetime.strptime(data['check_out'], '%Y-%m-%d').date()
            
            if check_in >= check_out:
                raise ValueError("Check-out date must be after check-in date")
            
            # Check room availability if room or dates changed
            room_id = data.get('room_id', existing['room_id'])
            if not cls.is_room_available(room_id, data['check_in'], data['check_out'], reservation_id):
                raise ValueError("Room is not available for the selected dates")
        
        # Prepare data for update
        update_data = {}
        if 'guest_id' in data:
            update_data['guest_id'] = data['guest_id']
        if 'room_id' in data:
            update_data['room_id'] = data['room_id']
        if 'check_in' in data:
            update_data['check_in'] = data['check_in']
        if 'check_out' in data:
            update_data['check_out'] = data['check_out']
        if 'notes' in data:
            update_data['notes'] = data['notes']
        if 'status' in data:
            if data['status'] not in cls.STATUS_CHOICES:
                raise ValueError(f"Invalid status: {data['status']}")
            update_data['status'] = data['status']
        
        success = cls.update(reservation_id, update_data)
        
        # Recalculate total if dates or room changed
        if success and ('check_in' in update_data or 'check_out' in update_data or 'room_id' in update_data):
            cls.update_reservation_total(reservation_id)
        
        return success
    
    @classmethod
    def update_reservation_total(cls, reservation_id: int) -> bool:
        """Recalculate and update reservation total price"""
        reservation = cls.get_by_id(reservation_id)
        if not reservation:
            return False
        
        # Calculate room total
        check_in = datetime.strptime(reservation['check_in'], '%Y-%m-%d').date()
        check_out = datetime.strptime(reservation['check_out'], '%Y-%m-%d').date()
        nights = (check_out - check_in).days
        room_total = float(reservation['room_price']) * nights
        
        # Calculate services total
        services_total = cls.get_services_total(reservation_id)
        
        total = room_total + services_total
        
        query = """
            UPDATE reservations 
            SET total_price = %s 
            WHERE reservation_id = %s
        """
        return DatabaseQuery.execute_query(query, (total, reservation_id))
    
    @classmethod
    def check_in(cls, reservation_id: int) -> bool:
        """Mark reservation as checked in"""
        reservation = cls.find(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        
        if reservation['status'] != 'CONFIRMED':
            raise ValueError(f"Cannot check in reservation with status: {reservation['status']}")
        
        # Update room status to OCCUPIED
        from models.room_model import RoomModel
        RoomModel.update_status(reservation['room_id'], 'OCCUPIED')
        
        return cls.update(reservation_id, {'status': 'CHECKED_IN'})
    
    @classmethod
    def check_out(cls, reservation_id: int) -> bool:
        """Mark reservation as checked out"""
        reservation = cls.find(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        
        if reservation['status'] != 'CHECKED_IN':
            raise ValueError(f"Cannot check out reservation with status: {reservation['status']}")
        
        # Update room status to AVAILABLE
        from models.room_model import RoomModel
        RoomModel.update_status(reservation['room_id'], 'AVAILABLE')
        
        return cls.update(reservation_id, {'status': 'CHECKED_OUT'})
    
    @classmethod
    def cancel_reservation(cls, reservation_id: int) -> bool:
        """Cancel a reservation"""
        reservation = cls.find(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        
        if reservation['status'] in ['CHECKED_OUT', 'CANCELLED']:
            raise ValueError(f"Cannot cancel {reservation['status']} reservation")
        
        # If checked in, update room status
        if reservation['status'] == 'CHECKED_IN':
            from models.room_model import RoomModel
            RoomModel.update_status(reservation['room_id'], 'AVAILABLE')
        
        return cls.update(reservation_id, {'status': 'CANCELLED'})
    
    @classmethod
    def delete_reservation(cls, reservation_id: int) -> bool:
        """Soft-delete a reservation (only CANCELLED or CHECKED_OUT allowed)"""
        reservation = cls.find(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")

        if reservation['status'] not in ['CANCELLED', 'CHECKED_OUT']:
            raise ValueError(f"Cannot delete reservation with status: {reservation['status']}. Only CANCELLED or CHECKED_OUT reservations can be deleted.")

        query = """
            UPDATE reservations
            SET is_deleted = TRUE
            WHERE reservation_id = %s
        """
        return DatabaseQuery.execute_query(query, (reservation_id,))

    @classmethod
    def is_room_available(cls, room_id: int, check_in: str, check_out: str, exclude_id: int = None) -> bool:
        """Check if room is available for given dates"""
        query = """
            SELECT COUNT(*) as count 
            FROM reservations 
            WHERE room_id = %s 
            AND status NOT IN ('CHECKED_OUT', 'CANCELLED')
            AND (
                (check_in <= %s AND check_out > %s)
                OR (check_in < %s AND check_out >= %s)
                OR (check_in >= %s AND check_out <= %s)
            )
        """
        params = [room_id, check_out, check_in, check_out, check_in, check_in, check_out]
        
        if exclude_id:
            query += " AND reservation_id != %s"
            params.append(exclude_id)
        
        result = DatabaseQuery.fetch_one(query, tuple(params))
        return result['count'] == 0 if result else True
    
    @classmethod
    def calculate_total(cls, room_id: int, nights: int, services: List[Dict] = None) -> float:
        """Calculate total price for reservation"""
        from models.room_model import RoomModel
        
        room = RoomModel.find(room_id)
        if not room:
            return 0.0
        
        room_total = float(room['price']) * nights
        
        services_total = 0.0
        if services:
            from models.service_model import ServiceModel
            for service in services:
                service_info = ServiceModel.find(service.get('service_id'))
                if service_info:
                    quantity = service.get('quantity', 1)
                    services_total += float(service_info['price']) * quantity
        
        return round(room_total + services_total, 2)
    
    @classmethod
    def get_services_total(cls, reservation_id: int) -> float:
        """Get total price of all services for a reservation"""
        query = """
            SELECT SUM(total) as total
            FROM reservation_services
            WHERE reservation_id = %s AND status != 'CANCELLED'
        """
        result = DatabaseQuery.fetch_one(query, (reservation_id,))
        return float(result['total']) if result and result['total'] else 0.0
    
    @classmethod
    def add_services_to_reservation(cls, reservation_id: int, services: List[Dict]) -> List[int]:
        """Add services to a reservation"""
        from models.service_model import ServiceModel
        
        added_ids = []
        for service in services:
            service_info = ServiceModel.find(service['service_id'])
            if not service_info:
                continue
            
            quantity = service.get('quantity', 1)
            unit_price = float(service_info['price'])
            total = unit_price * quantity
            
            query = """
                INSERT INTO reservation_services 
                (reservation_id, service_id, quantity, unit_price, total, status)
                VALUES (%s, %s, %s, %s, %s, 'PENDING')
            """
            result = DatabaseQuery.insert_and_get_id(
                query, 
                (reservation_id, service['service_id'], quantity, unit_price, total)
            )
            if result:
                added_ids.append(result)
        
        return added_ids
    
    @classmethod
    def get_reservation_services(cls, reservation_id: int) -> List[Dict[str, Any]]:
        """Get all services for a reservation"""
        query = """
            SELECT 
                rs.res_service_id as id,
                rs.service_id,
                s.name as service_name,
                rs.quantity,
                rs.unit_price,
                rs.total,
                rs.scheduled_at,
                rs.duration,
                rs.status
            FROM reservation_services rs
            JOIN services s ON rs.service_id = s.service_id
            WHERE rs.reservation_id = %s
            ORDER BY rs.created_at DESC
        """
        return DatabaseQuery.fetch_all(query, (reservation_id,))
    
    @classmethod
    def cancel_service_booking(cls, booking_id: int) -> bool:
        """Cancel a service booking"""
        query = """
            UPDATE reservation_services 
            SET status = 'CANCELLED' 
            WHERE res_service_id = %s
        """
        success = DatabaseQuery.execute_query(query, (booking_id,))
        
        if success:
            # Get reservation_id and update total
            res_query = "SELECT reservation_id FROM reservation_services WHERE res_service_id = %s"
            result = DatabaseQuery.fetch_one(res_query, (booking_id,))
            if result:
                cls.update_reservation_total(result['reservation_id'])
        
        return success
    
    @classmethod
    def get_today_reservations(cls) -> List[Dict[str, Any]]:
        """Get reservations for today"""
        today = date.today().strftime('%Y-%m-%d')
        query = """
            SELECT 
                r.reservation_id as id,
                CONCAT(g.first_name, ' ', g.last_name) as guest_name,
                rm.room_number,
                r.check_in,
                r.check_out,
                r.status
            FROM reservations r
            JOIN guests g ON r.guest_id = g.guest_id
            JOIN rooms rm ON r.room_id = rm.room_id
            WHERE r.check_in <= %s AND r.check_out >= %s
            ORDER BY r.check_in
        """
        return DatabaseQuery.fetch_all(query, (today, today))