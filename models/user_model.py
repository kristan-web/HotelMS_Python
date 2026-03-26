"""
User Model
===========
Handles all DB operations for the `users` table.
Supports soft-delete (is_deleted flag).
"""

from utils.db_connection import get_connection


class UserModel:

    # ── CREATE ────────────────────────────────────────────────────────────────
    @staticmethod
    def create(first_name: str, last_name: str, email: str,
               phone: str, password_hash: str, role: str) -> bool:
        """Insert a new user. Returns True on success."""
        sql = """
            INSERT INTO users (first_name, last_name, email, phone, password, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (first_name, last_name, email, phone,
                              password_hash, role))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[UserModel.create] {e}")
            return False

    # ── READ ──────────────────────────────────────────────────────────────────
    @staticmethod
    def get_all_active() -> list:
        """Return all non-deleted users."""
        sql = """
            SELECT user_id, first_name, last_name, email, phone, role,
                   created_at, updated_at
            FROM users
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
            print(f"[UserModel.get_all_active] {e}")
            return []

    @staticmethod
    def get_all_deleted() -> list:
        """Return all soft-deleted users."""
        sql = """
            SELECT user_id, first_name, last_name, email, phone, role
            FROM users
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
            print(f"[UserModel.get_all_deleted] {e}")
            return []

    @staticmethod
    def get_by_id(user_id: int) -> dict | None:
        """Return a single user by ID (including deleted)."""
        sql = """
            SELECT user_id, first_name, last_name, email, phone, role,
                   is_deleted, created_at
            FROM users WHERE user_id = %s
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (user_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[UserModel.get_by_id] {e}")
            return None

    @staticmethod
    def get_by_email(email: str) -> dict | None:
        """Return a user by email (used for login)."""
        sql = """
            SELECT user_id, first_name, last_name, email, phone,
                   password, role, is_deleted
            FROM users WHERE email = %s
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (email,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[UserModel.get_by_email] {e}")
            return None

    # ── UPDATE ────────────────────────────────────────────────────────────────
    @staticmethod
    def update(user_id: int, first_name: str, last_name: str,
               email: str, phone: str, role: str) -> bool:
        """Update user details. Returns True on success."""
        sql = """
            UPDATE users
            SET first_name=%s, last_name=%s, email=%s, phone=%s, role=%s
            WHERE user_id=%s AND is_deleted=0
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (first_name, last_name, email, phone,
                              role, user_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[UserModel.update] {e}")
            return False

    @staticmethod
    def update_password(user_id: int, password_hash: str) -> bool:
        """Update a user's password hash."""
        sql = "UPDATE users SET password=%s WHERE user_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (password_hash, user_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[UserModel.update_password] {e}")
            return False

    # ── SOFT DELETE / RESTORE ─────────────────────────────────────────────────
    @staticmethod
    def soft_delete(user_id: int) -> bool:
        """Mark a user as deleted."""
        sql = "UPDATE users SET is_deleted=1 WHERE user_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[UserModel.soft_delete] {e}")
            return False

    @staticmethod
    def restore(user_id: int) -> bool:
        """Restore a soft-deleted user."""
        sql = "UPDATE users SET is_deleted=0 WHERE user_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (user_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[UserModel.restore] {e}")
            return False

    # ── HELPERS ───────────────────────────────────────────────────────────────
    @staticmethod
    def email_exists(email: str, exclude_id: int = None) -> bool:
        """Check if an email is already in use (optionally excluding a user_id)."""
        if exclude_id:
            sql = "SELECT 1 FROM users WHERE email=%s AND user_id != %s"
            params = (email, exclude_id)
        else:
            sql = "SELECT 1 FROM users WHERE email=%s"
            params = (email,)
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, params)
            exists = cur.fetchone() is not None
            cur.close()
            return exists
        except Exception as e:
            print(f"[UserModel.email_exists] {e}")
            return False