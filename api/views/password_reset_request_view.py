from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from datetime import timedelta
import uuid
from ..serializers.password_reset_request_serializer import PasswordResetRequestSerializer
from ..models.password_reset_token import PasswordResetToken

User = get_user_model()

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                return Response({'detail': 'If the email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)
            # Update or create a password reset token for this user
            token_obj, _ = PasswordResetToken.objects.update_or_create(
                user=user,
                used=False,
                defaults={
                    'token': uuid.uuid4(),
                    'expiry': timezone.now() + timedelta(minutes=10),
                    'used': False,
                }
            )
            reset_url = request.build_absolute_uri(
                reverse('api:password-reset-confirm') + f'?token={token_obj.token}'
            )
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            return Response({'detail': 'If the email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
