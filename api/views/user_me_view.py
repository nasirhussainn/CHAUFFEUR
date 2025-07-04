from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from ..serializers.user_serializer import UserSerializer

class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response({
            "message": "User info fetched successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
