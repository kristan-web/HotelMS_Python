"""
Room Model
===========
Handles all DB operations for the `rooms` table.
"""

from utils.db_connection import get_connection


class RoomModel:

    @staticmethod
    def create(room_number: str, room_type: str, price: float,
               capacity: int, description: str = "") -> bool:
        sql = """
            INSERT INTO rooms (room_number, room_type, price, capacity, description)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (room_number, room_type, price,
                              capacity, description))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[RoomModel.create] {e}")
            return False

    @staticmethod
    def get_all() -> list:
        sql = """
            SELECT room_id, room_number, room_type, price, capacity,
                   status, description
            FROM rooms
            ORDER BY room_number
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[RoomModel.get_all] {e}")
            return []

    @staticmethod
    def get_available(check_in: str, check_out: str) -> list:
        """
        Return rooms not already booked in the given date range
        (CONFIRMED or CHECKED_IN reservations).
        """
        sql = """
            SELECT r.room_id, r.room_number, r.room_type,
                   r.price, r.capacity, r.description
            FROM rooms r
            WHERE r.status = 'AVAILABLE'
              AND r.room_id NOT IN (
                  SELECT res.room_id FROM reservations res
                  WHERE res.status IN ('CONFIRMED','CHECKED_IN')
                    AND NOT (res.check_out <= %s OR res.check_in >= %s)
              )
            ORDER BY r.room_number
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (check_in, check_out))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[RoomModel.get_available] {e}")
            return []

    @staticmethod
    def get_by_id(room_id: int) -> dict | None:
        sql = "SELECT * FROM rooms WHERE room_id = %s"
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (room_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[RoomModel.get_by_id] {e}")
            return None

    @staticmethod
    def update(room_id: int, room_number: str, room_type: str,
               price: float, capacity: int, description: str) -> bool:
        sql = """
            UPDATE rooms
            SET room_number=%s, room_type=%s, price=%s,
                capacity=%s, description=%s
            WHERE room_id=%s
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (room_number, room_type, price,
                              capacity, description, room_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[RoomModel.update] {e}")
            return False

    @staticmethod
    def update_status(room_id: int, status: str) -> bool:
        sql = "UPDATE rooms SET status=%s WHERE room_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (status, room_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[RoomModel.update_status] {e}")
            return False

    @staticmethod
    def delete(room_id: int) -> bool:
        sql = "DELETE FROM rooms WHERE room_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (room_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[RoomModel.delete] {e}")
            return False