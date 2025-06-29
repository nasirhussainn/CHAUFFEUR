from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models.password_reset_token import PasswordResetToken
from ..serializers.password_reset_confirm_serializer import PasswordResetConfirmSerializer

User = get_user_model()

class PasswordResetConfirmView(APIView):
    def get(self, request):
        try:
            token = request.GET.get('token')
            if not token:
                return Response({'message': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                token_obj = PasswordResetToken.objects.get(token=token, used=False)
            except PasswordResetToken.DoesNotExist:
                return Response({'message': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

            if token_obj.is_expired():
                return Response({'message': 'Token expired. Please request a new password reset.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Token is valid.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'message': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']

            try:
                token_obj = PasswordResetToken.objects.get(token=token, used=False)
            except PasswordResetToken.DoesNotExist:
                return Response({'message': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)

            if token_obj.is_expired():
                return Response({'message': 'Token expired. Please request a new password reset.'}, status=status.HTTP_400_BAD_REQUEST)

            user = token_obj.user
            user.set_password(new_password)
            user.save()

            token_obj.used = True
            token_obj.save()

            return Response({'message': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)

        # Serializer errors handled by renderer (data field)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
