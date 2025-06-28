from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from ..models.password_reset_token import PasswordResetToken
from ..serializers.password_reset_confirm_serializer import PasswordResetConfirmSerializer

User = get_user_model()

# Set the email backend to console for development
settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

class PasswordResetConfirmView(APIView):
    def get(self, request):
        try:
            token = request.GET.get('token')
            if not token:
                return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                token_obj = PasswordResetToken.objects.get(token=token, used=False)
            except PasswordResetToken.DoesNotExist:
                return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
            if token_obj.is_expired():
                return Response({'detail': 'Token expired. Please request a new password reset.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'detail': 'Token is valid.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': f'Unexpected error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            try:
                token_obj = PasswordResetToken.objects.get(token=token, used=False)
            except PasswordResetToken.DoesNotExist:
                return Response({'detail': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)
            if token_obj.is_expired():
                return Response({'detail': 'Token expired. Please request a new password reset.'}, status=status.HTTP_400_BAD_REQUEST)
            user = token_obj.user
            user.set_password(new_password)
            user.save()
            token_obj.used = True
            token_obj.save()
            return Response({'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
