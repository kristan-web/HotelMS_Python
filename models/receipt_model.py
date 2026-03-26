"""
Receipt Model
==============
Handles all DB operations for the `receipts` table.
"""

from utils.db_connection import get_connection


class ReceiptModel:

    @staticmethod
    def create(reservation_id: int, subtotal: float,
               tax: float, total: float) -> str | None:
        """
        Create a receipt for a reservation.
        Auto-generates a receipt number (RCP-XXXXXX).
        Returns the receipt_number string, or None on failure.
        """
        receipt_number = ReceiptModel._generate_number()
        sql = """
            INSERT INTO receipts
                (reservation_id, receipt_number, subtotal, tax, total)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (reservation_id, receipt_number,
                              subtotal, tax, total))
            conn.commit()
            cur.close()
            return receipt_number
        except Exception as e:
            print(f"[ReceiptModel.create] {e}")
            return None

    @staticmethod
    def get_by_reservation(reservation_id: int) -> dict | None:
        sql = """
            SELECT rc.receipt_id, rc.receipt_number, rc.subtotal,
                   rc.tax, rc.total, rc.issued_at,
                   r.check_in, r.check_out, r.nights, r.total_price,
                   CONCAT(g.first_name,' ',g.last_name) AS guest_name,
                   g.address AS guest_address,
                   ro.room_number, ro.room_type
            FROM receipts rc
            JOIN reservations r ON r.reservation_id = rc.reservation_id
            JOIN guests g       ON g.guest_id        = r.guest_id
            JOIN rooms ro       ON ro.room_id         = r.room_id
            WHERE rc.reservation_id = %s
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (reservation_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[ReceiptModel.get_by_reservation] {e}")
            return None

    @staticmethod
    def get_by_id(receipt_id: int) -> dict | None:
        sql = "SELECT * FROM receipts WHERE receipt_id = %s"
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (receipt_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[ReceiptModel.get_by_id] {e}")
            return None

    @staticmethod
    def _generate_number() -> str:
        """Generate a unique receipt number like RCP-000123."""
        sql = "SELECT COUNT(*) AS cnt FROM receipts"
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            row = cur.fetchone()
            cur.close()
            count = (row["cnt"] if row else 0) + 1
            return f"RCP-{count:06d}"
        except Exception:
            import random
            return f"RCP-{random.randint(100000, 999999)}"