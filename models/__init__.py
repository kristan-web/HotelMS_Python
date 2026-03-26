"""
Models package for Hotel Management System
Contains database models for all entities
"""

from models.base_model import BaseModel
from models.service_model import ServiceModel

__all__ = [
    'BaseModel',
    'ServiceModel',
]