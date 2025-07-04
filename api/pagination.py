from rest_framework.pagination import PageNumberPagination

class DynamicPageNumberPagination(PageNumberPagination):
    page_size = 10  # default
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def paginate_queryset(self, queryset, request, view=None):
        if request.query_params.get('all') == 'true':
            return None  # disables pagination when ?all=true
        return super().paginate_queryset(queryset, request, view)
