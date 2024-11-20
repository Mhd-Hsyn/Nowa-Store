from rest_framework.pagination import PageNumberPagination

class BrandPagination(PageNumberPagination):
    page_size = 5  # Number of items per page
    page_size_query_param = 'page_size'  # Allow clients to set page size via query parameter
    max_page_size = 100  # Maximum limit for page size


class ProductCategoryPagination(PageNumberPagination):
    page_size = 5  # Number of items per page
    page_size_query_param = 'page_size'  # Allow clients to set page size via query parameter
    max_page_size = 100  # Maximum limit for page size
