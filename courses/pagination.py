from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CategoryPagination(PageNumberPagination):
    """
    Custom pagination for categories with page and page_size parameters.
    """

    page_size = 10  # Default page size
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({"total_category": self.page.paginator.count, "result": data})
