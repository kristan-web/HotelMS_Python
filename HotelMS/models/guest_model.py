"""
Guest Model
============
Handles all DB operations for the `guests` table.
Supports soft-delete (is_deleted flag).
"""

from utils.db_connection import get_connection


class GuestModel:

    # ── CREATE ────────────────────────────────────────────────────────────────
    @staticmethod
    def create(first_name: str, last_name: str, email: str,
               phone: str, address: str) -> bool:
        """Insert a new guest. Returns True on success."""
        sql = """
            INSERT INTO guests (first_name, last_name, email, phone, address)
            VALUES (%s, %s, %s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (first_name, last_name, email, phone, address))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[GuestModel.create] {e}")
            return False

    # ── READ ──────────────────────────────────────────────────────────────────
    @staticmethod
    def get_all_active() -> list:
        """Return all non-deleted guests."""
        sql = """
            SELECT guest_id, first_name, last_name, email, phone, address,
                   created_at, updated_at
            FROM guests
            WHERE is_deleted = 0
            ORDER BY last_name, first_name
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[GuestModel.get_all_active] {e}")
            return []

    @staticmethod
    def get_all_deleted() -> list:
        """Return all soft-deleted guests."""
        sql = """
            SELECT guest_id, first_name, last_name, email, phone, address
            FROM guests
            WHERE is_deleted = 1
            ORDER BY last_name, first_name
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[GuestModel.get_all_deleted] {e}")
            return []

    @staticmethod
    def get_by_id(guest_id: int) -> dict | None:
        sql = """
            SELECT guest_id, first_name, last_name, email, phone, address
            FROM guests WHERE guest_id = %s
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (guest_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[GuestModel.get_by_id] {e}")
            return None

    # ── UPDATE ────────────────────────────────────────────────────────────────
    @staticmethod
    def update(guest_id: int, first_name: str, last_name: str,
               email: str, phone: str, address: str) -> bool:
        sql = """
            UPDATE guests
            SET first_name=%s, last_name=%s, email=%s, phone=%s, address=%s
            WHERE guest_id=%s AND is_deleted=0
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (first_name, last_name, email, phone,
                              address, guest_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[GuestModel.update] {e}")
            return False

    # ── SOFT DELETE / RESTORE ─────────────────────────────────────────────────
    @staticmethod
    def soft_delete(guest_id: int) -> bool:
        sql = "UPDATE guests SET is_deleted=1 WHERE guest_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (guest_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[GuestModel.soft_delete] {e}")
            return False

    @staticmethod
    def restore(guest_id: int) -> bool:
        sql = "UPDATE guests SET is_deleted=0 WHERE guest_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (guest_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[GuestModel.restore] {e}")
            return False

    @staticmethod
    def email_exists(email: str, exclude_id: int = None) -> bool:
        if exclude_id:
            sql = "SELECT 1 FROM guests WHERE email=%s AND guest_id != %s AND is_deleted=0"
            params = (email, exclude_id)
        else:
            sql = "SELECT 1 FROM guests WHERE email=%s AND is_deleted=0"
            params = (email,)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, params)
            exists = cur.fetchone() is not None
            cur.close()
            return exists
        except Exception as e:
            print(f"[GuestModel.email_exists] {e}")
            return False