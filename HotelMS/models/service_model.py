"""
Service Model
==============
Handles all DB operations for the `services` table.
Supports soft-delete (is_deleted flag).
"""

from utils.db_connection import get_connection


class ServiceModel:

    @staticmethod
    def create(name: str, price: float, duration: int,
               status: str = "Active") -> bool:
        sql = """
            INSERT INTO services (name, price, duration, status)
            VALUES (%s, %s, %s, %s)
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (name, price, duration, status))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[ServiceModel.create] {e}")
            return False

    @staticmethod
    def get_all_active() -> list:
        sql = """
            SELECT service_id, name, price, duration, status
            FROM services
            WHERE is_deleted = 0
            ORDER BY name
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[ServiceModel.get_all_active] {e}")
            return []

    @staticmethod
    def get_all_deleted() -> list:
        sql = """
            SELECT service_id, name, price, duration, status
            FROM services
            WHERE is_deleted = 1
            ORDER BY name
        """
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            return rows
        except Exception as e:
            print(f"[ServiceModel.get_all_deleted] {e}")
            return []

    @staticmethod
    def get_by_id(service_id: int) -> dict | None:
        sql = "SELECT * FROM services WHERE service_id = %s"
        try:
            conn = get_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute(sql, (service_id,))
            row = cur.fetchone()
            cur.close()
            return row
        except Exception as e:
            print(f"[ServiceModel.get_by_id] {e}")
            return None

    @staticmethod
    def update(service_id: int, name: str, price: float,
               duration: int, status: str) -> bool:
        sql = """
            UPDATE services
            SET name=%s, price=%s, duration=%s, status=%s
            WHERE service_id=%s AND is_deleted=0
        """
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (name, price, duration, status, service_id))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[ServiceModel.update] {e}")
            return False

    @staticmethod
    def soft_delete(service_id: int) -> bool:
        sql = "UPDATE services SET is_deleted=1 WHERE service_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (service_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[ServiceModel.soft_delete] {e}")
            return False

    @staticmethod
    def restore(service_id: int) -> bool:
        sql = "UPDATE services SET is_deleted=0 WHERE service_id=%s"
        try:
            conn = get_connection()
            cur = conn.cursor()
            cur.execute(sql, (service_id,))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            print(f"[ServiceModel.restore] {e}")
            return False