"""
Custom renderers for SmartCart API.

Wraps all JSON responses in a consistent envelope format.
"""
from rest_framework.renderers import JSONRenderer


class SmartCartJSONRenderer(JSONRenderer):
    """
    Custom JSON renderer that wraps responses in a consistent format.

    Success response:
    {
        "success": true,
        "message": "...",
        "data": { ... }
    }

    Error response:
    {
        "success": false,
        "message": "...",
        "errors": { ... }
    }

    Note: Paginated responses are handled by StandardResultsSetPagination
    and already include the success flag.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response') if renderer_context else None

        if response is None:
            return super().render(data, accepted_media_type, renderer_context)

        # Don't wrap if data is already in our format (e.g., from pagination)
        if isinstance(data, dict) and 'success' in data:
            return super().render(data, accepted_media_type, renderer_context)

        # Don't wrap schema/docs responses
        if response.status_code == 200 and isinstance(data, (dict, list)):
            view = renderer_context.get('view')
            if view and getattr(view, 'schema', None):
                # Check if this is a schema view
                view_class_name = view.__class__.__name__
                if 'Spectacular' in view_class_name:
                    return super().render(data, accepted_media_type, renderer_context)

        # Determine if this is an error response
        is_error = response.status_code >= 400

        if is_error:
            wrapped = {
                'success': False,
                'message': self._extract_message(data, is_error=True),
                'errors': data if isinstance(data, dict) else {'detail': data},
            }
        else:
            wrapped = {
                'success': True,
                'message': self._extract_message(data, is_error=False),
                'data': data,
            }

        return super().render(wrapped, accepted_media_type, renderer_context)

    @staticmethod
    def _extract_message(data, is_error=False):
        """
        Extract a human-readable message from response data.
        """
        if isinstance(data, dict):
            # Try common message fields
            for key in ('message', 'detail', 'msg'):
                if key in data:
                    msg = data[key]
                    return str(msg) if not isinstance(msg, list) else str(msg[0])
        if isinstance(data, str):
            return data
        if isinstance(data, list) and data:
            return str(data[0])
        return 'An error occurred.' if is_error else 'Success'
