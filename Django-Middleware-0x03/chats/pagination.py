# chats/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages with:
    - 20 messages per page
    - Total count in response
    - Standard pagination controls
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # Total item count
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'per_page': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'integer',
                    'example': 123,
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/messages/?page=2'
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                    'format': 'uri',
                    'example': 'http://api.example.org/messages/'
                },
                'results': schema,
                'per_page': {
                    'type': 'integer',
                    'example': 20
                },
                'total_pages': {
                    'type': 'integer',
                    'example': 7
                },
                'current_page': {
                    'type': 'integer',
                    'example': 1
                }
            }
        }