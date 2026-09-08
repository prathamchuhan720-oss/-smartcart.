"""
Pagination classes for SmartCart API.

Provides consistent pagination across all list endpoints.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with configurable page size.

    Usage:
        GET /api/products/?page=2&page_size=10

    Response includes:
        - count: Total number of results
        - total_pages: Total number of pages
        - current_page: Current page number
        - page_size: Number of items per page
        - next: URL for next page
        - previous: URL for previous page
        - results: List of items
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.get_page_size(self.request),
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
