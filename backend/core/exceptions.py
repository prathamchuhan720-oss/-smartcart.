"""
Custom exception handler for SmartCart API.

Provides consistent error response format across all API endpoints.
"""
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    ValidationError as DRFValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger('smartcart')


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns consistent JSON error responses.

    Response format:
    {
        "success": false,
        "message": "Human-readable error message",
        "errors": {
            "field_name": ["Error detail"]
        }
    }
    """
    # Convert Django ValidationError to DRF ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            exc = DRFValidationError(detail=exc.message_dict)
        else:
            exc = DRFValidationError(detail=exc.messages)

    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Determine the error message
        if isinstance(exc, NotAuthenticated):
            message = 'Authentication credentials were not provided.'
        elif isinstance(exc, AuthenticationFailed):
            message = 'Invalid authentication credentials.'
        elif isinstance(exc, PermissionDenied):
            message = 'You do not have permission to perform this action.'
        elif isinstance(exc, Http404):
            message = 'Resource not found.'
        elif isinstance(exc, DRFValidationError):
            message = 'Validation failed.'
        else:
            message = str(exc.detail) if hasattr(exc, 'detail') else 'An error occurred.'

        # Build consistent error response
        error_data = {
            'success': False,
            'message': message,
            'errors': _format_errors(response.data),
        }

        response.data = error_data
    else:
        # Unhandled exceptions (500 errors)
        logger.exception(
            f'Unhandled exception in {context.get("view", "unknown view")}',
            exc_info=exc,
        )
        response = Response(
            {
                'success': False,
                'message': 'An internal server error occurred.',
                'errors': {},
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _format_errors(data):
    """
    Ensure errors are always returned as a dictionary.
    """
    if isinstance(data, dict):
        formatted = {}
        for key, value in data.items():
            if isinstance(value, list):
                formatted[key] = [str(v) for v in value]
            elif isinstance(value, str):
                formatted[key] = [value]
            else:
                formatted[key] = [str(value)]
        return formatted
    if isinstance(data, list):
        return {'non_field_errors': [str(item) for item in data]}
    return {'detail': [str(data)]}
