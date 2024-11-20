from rest_framework.response import Response
#from rest_framework import PageNumberPagination
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 10
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })
    

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'  
    max_page_size = 100  

