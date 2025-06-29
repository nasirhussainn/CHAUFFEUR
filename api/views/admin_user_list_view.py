from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from ..serializers.admin_user_list_serializer import AdminUserListSerializer

User = get_user_model()

class AdminUserListView(APIView):

    def get(self, request):
        users = User.objects.all()
        serializer = AdminUserListSerializer(users, many=True)
        return Response({
            "message": "User list fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
