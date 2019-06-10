from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from django.conf import settings


class ProjectPageNumberPagination(PageNumberPagination):
	page_size = settings.PAGINATION_PAGESIZE
	max_page_size = 500


class ProjectLimitOffsetPagination(LimitOffsetPagination):
	default_limit = settings.PAGINATION_PAGESIZE
	max_limit = 100