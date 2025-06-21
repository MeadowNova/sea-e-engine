"""
Authentication module for SEA-E Engine.
"""

from .google_oauth import GoogleOAuthManager, get_authenticated_services

__all__ = ['GoogleOAuthManager', 'get_authenticated_services']
