"""
Reservation Model
==================
Handles all DB operations for the `reservations` and
`reservation_services` tables.
"""

from utils.db_connection import get_connection


class ReservationModel:

    # ── CREATE ────────────────────────────────────────────────────────────────
    @staticmethod
    def create(guest_id: int, room_id: int, user_id: int,
               check_in: str, check_out: str,
               total_price: float, notes: str = "") -> int | None:
        """
        Insert a new reservation.
        Returns the new reservation_id, or None on failure.
        """
        sql = """
            INSERT INTO reservations
                (guest_id, room_id, user_id, check_in, check_out,
                 total_price, notes, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'CONFIRMED')
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (guest_id, room_id, user_id,
                              check_in, check_out, total_price, notes))
            conn.commit()
            new_id = cur.lastrowid
            cur.close()
            return new_id
        except Exception as e:
            print(f"[ReservationModel.create] {e}")
            return None

    # ── READ ──────────────────────────────────────────────────────────────────
    @staticmethod
    def get_all(status_filter: str = "ALL") -> list:
        """Return all reservations, optionally filtered by status."""
        if status_filter == "ALL":
            sql = """
                SELECT r.reservation_id, r.check_in, r.check_out,
                       r.nights, r.total_price, r.notes, r.status,
                       r.created_at,
                       CONCAT(g.first_name,' ',g.last_name) AS guest_name,
                       g.guest_id,
                       ro.room_number, ro.room_type, ro.room_id
                FROM reservations r
                JOIN guests g  ON g.guest_id = r.guest_id
                JOIN rooms  ro ON ro.room_id  = r.room_id
                ORDER BY r.created_at DESC
            """
            params = ()
        else:
            sql = """
                SELECT r.reservation_id, r.check_in, r.check_out,
                       r.nights, r.total_price, r.notes, r.status,
                       r.created_at,
                       CONCAT(g.first_name,' ',g.last_name) AS guest_name,
                       g.guest_id,
                       ro.room_number, ro.room_type, ro.room_id
                FROM reservations r
                JOIN guests g  ON g.guest_id = r.guest_id
                JOIN rooms  ro ON ro.room_id  = r.room_id
                WHERE r.status = %s
                ORDER BY r.created_at DESC
            """
            params = (status_filter,)
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[ReservationModel.get_all] {e}")
            return []

    @staticmethod
    def get_by_id(reservation_id: int) -> dict | None:
        sql = """
            SELECT r.*, 
                   CONCAT(g.first_name,' ',g.last_name) AS guest_name,
                   ro.room_number, ro.room_type, ro.price AS room_price
            FROM reservations r
            JOIN guests g  ON g.guest_id = r.guest_id
            JOIN rooms  ro ON ro.room_id  = r.room_id
            WHERE r.reservation_id = %s
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (reservation_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[ReservationModel.get_by_id] {e}")
            return None

    @staticmethod
    def get_today_stats() -> dict:
        """Return today's reservation count, check-ins, check-outs."""
        sql = """
            SELECT
                SUM(status IN ('CONFIRMED','CHECKED_IN'))  AS reservations,
                SUM(status = 'CHECKED_IN'
                    AND check_in = CURDATE())               AS checkins,
                SUM(status = 'CHECKED_OUT'
                    AND check_out = CURDATE())              AS checkouts,
                SUM(CASE WHEN status='CHECKED_OUT'
                         AND check_out = CURDATE()
                         THEN total_price ELSE 0 END)       AS revenue
            FROM reservations
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            row = cur.fetchone()
            cur.close()
            return row or {"reservations": 0, "checkins": 0,
                           "checkouts": 0, "revenue": 0}
        except Exception as e:
            print(f"[ReservationModel.get_today_stats] {e}")
            return {"reservations": 0, "checkins": 0,
                    "checkouts": 0, "revenue": 0}

    # ── UPDATE STATUS ─────────────────────────────────────────────────────────
    @staticmethod
    def update_status(reservation_id: int, status: str) -> bool:
        sql = "UPDATE reservations SET status=%s WHERE reservation_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (status, reservation_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[ReservationModel.update_status] {e}")
            return False

    # ── RESERVATION SERVICES ──────────────────────────────────────────────────
    @staticmethod
    def add_service(reservation_id: int, service_id: int,
                    quantity: int, unit_price: float,
                    discount: float = 0.0, tax: float = 0.0,
                    scheduled_at: str = None,
                    duration: int = 0) -> bool:
        total = (unit_price * quantity) - discount + tax
        sql = """
            INSERT INTO reservation_services
                (reservation_id, service_id, quantity, unit_price,
                 discount, tax, total, scheduled_at, duration)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (reservation_id, service_id, quantity,
                              unit_price, discount, tax, total,
                              scheduled_at, duration))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[ReservationModel.add_service] {e}")
            return False

    @staticmethod
    def get_services(reservation_id: int) -> list:
        sql = """
            SELECT rs.res_service_id, rs.quantity, rs.unit_price,
                   rs.discount, rs.tax, rs.total, rs.scheduled_at,
                   rs.duration, rs.status,
                   s.name AS service_name, s.service_id
            FROM reservation_services rs
            JOIN services s ON s.service_id = rs.service_id
            WHERE rs.reservation_id = %s
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (reservation_id,))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[ReservationModel.get_services] {e}")
            return []