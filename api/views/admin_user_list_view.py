from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers.admin_user_list_serializer import AdminUserListSerializer
from api.pagination import DynamicPageNumberPagination

User = get_user_model()

class AdminUserListView(APIView):
    pagination_class = DynamicPageNumberPagination

    def get(self, request):
        users = User.objects.all()
        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users, request, view=self)

        serializer = AdminUserListSerializer(paginated_users or users, many=True)

        if paginated_users is not None:
            return paginator.get_paginated_response({
                "message": "User list fetched successfully.",
                "data": serializer.data
            })

        # No pagination applied (e.g. ?all=true)
        return Response({
            "message": "User list fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

