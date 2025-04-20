from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that allows client to specify page size.
    """
    page_size = 10  # Default page size
    page_size_query_param = 'page_size'  # Allow client to override using this query parameter
    max_page_size = 100  # Maximum page size limit
    
    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.get_page_size(self.request),
            'results': data
        }) 