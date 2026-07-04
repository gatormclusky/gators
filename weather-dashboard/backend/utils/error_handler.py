"""
Error handling utilities
"""

from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base API error class"""
    
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def handle_error(error: APIError):
    """Handle API errors"""
    logger.error(f"API Error: {error.message} (Status: {error.status_code})")
    
    return jsonify({
        'status': 'error',
        'message': error.message,
        'code': error.status_code
    }), error.status_code
