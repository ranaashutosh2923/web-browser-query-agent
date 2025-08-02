"""
API package for Web Browser Query Agent
Contains Flask routes and API endpoints
"""

from .routes import create_app

__all__ = ['create_app']
