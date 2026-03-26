"""
Configuration package for Hotel Management System
Contains database connection and configuration utilities
"""

from config.database import (
    DatabaseConfig,
    DatabaseConnection,
    DatabaseQuery,
    test_connection
)

__all__ = [
    'DatabaseConfig',
    'DatabaseConnection',
    'DatabaseQuery',
    'test_connection'
]