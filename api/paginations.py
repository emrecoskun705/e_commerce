from rest_framework import pagination

class SearchProductPagination(pagination.PageNumberPagination):
    page_size = 14
    page_size_query_param = 'page_size'
    max_page_size = 20