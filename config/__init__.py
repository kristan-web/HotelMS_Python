"""
Config package initialization
Exports database configuration and connection functions
"""

from .database import (
    get_connection,
    test_connection,
    execute_query,
    execute_query_with_commit,
    get_one,
    insert_one,
    DB_CONFIG,
    DatabaseQuery  # Add this line
)

# For backward compatibility with any code expecting DatabaseConfig
DatabaseConfig = DB_CONFIG

__all__ = [
    'get_connection',
    'test_connection', 
    'execute_query',
    'execute_query_with_commit',
    'get_one',
    'insert_one',
    'DB_CONFIG',
    'DatabaseConfig',  # Alias for backward compatibility
    'DatabaseQuery'    # Add this line
]