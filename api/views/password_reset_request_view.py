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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.url_helpers import build_full_url


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
            path = reverse('api:password-reset-confirm') + f'?token={token_obj.token}'
            reset_url = build_full_url(request, path)
            subject = 'Password Reset Request'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [user.email]
            context = {
                'user': user,
                'reset_url': reset_url,
            }

            text_content = f"Hi {user.first_name or 'User'},\n\nYou can reset your password using the link below:\n{reset_url}\n\nIf you didn't request this, please ignore this message."
            html_content = render_to_string('emails/password_reset_email.html', context)

            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send()

            return Response({'detail': 'If the email exists, a reset link has been sent.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
