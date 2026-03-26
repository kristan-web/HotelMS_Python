"""
Admin Log Model
================
Handles all DB operations for the `admin_logs` table.
"""

from utils.db_connection import get_connection


class AdminLogModel:

    @staticmethod
    def log(user_id: int, action: str, description: str = "") -> bool:
        """Insert an activity log entry."""
        sql = """
            INSERT INTO admin_logs (user_id, action, description)
            VALUES (%s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (user_id, action, description))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[AdminLogModel.log] {e}")
            return False

    @staticmethod
    def get_all() -> list:
        """Return all logs, newest first."""
        sql = """
            SELECT al.log_id, al.action, al.description, al.logged_at,
                   CONCAT(u.first_name,' ',u.last_name) AS user_name,
                   u.role
            FROM admin_logs al
            JOIN users u ON u.user_id = al.user_id
            ORDER BY al.logged_at DESC
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[AdminLogModel.get_all] {e}")
            return []

    @staticmethod
    def get_by_user(user_id: int) -> list:
        sql = """
            SELECT log_id, action, description, logged_at
            FROM admin_logs
            WHERE user_id = %s
            ORDER BY logged_at DESC
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[AdminLogModel.get_by_user] {e}")
            return []