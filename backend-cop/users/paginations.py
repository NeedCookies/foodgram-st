# Сторонние библиотеки
from rest_framework.pagination import PageNumberPagination

# Наш (локальный) импорт
from constants import DEFAULT_PAGE_SIZE


class UserPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "limit"
