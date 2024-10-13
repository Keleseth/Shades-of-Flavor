from rest_framework.pagination import PageNumberPagination


class LimitNumberPagination(PageNumberPagination):
    """Класс пагинации с доп. параметром limit."""

    page_size_query_param = 'limit'
