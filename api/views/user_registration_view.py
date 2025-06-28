from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from datetime import timedelta
from ..serializers.user_registration_serializer import UserRegistrationSerializer
from ..models.email_verification import EmailVerification
from django.contrib.auth import get_user_model
from django.db import transaction
import uuid

# For development, use Django console email backend
settings.EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

User = get_user_model()

class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    email = serializer.validated_data['email']
                    user_qs = User.objects.filter(email=email)
                    if user_qs.exists():
                        user = user_qs.first()
                        if not user.is_active:
                            # User exists but is inactive, update verification
                            verification, _ = EmailVerification.objects.get_or_create(user=user)
                            verification.token = uuid.uuid4()
                            verification.expiry = timezone.now() + timedelta(minutes=10)
                            verification.is_verified = False
                            verification.save()
                            verification_url = request.build_absolute_uri(
                                reverse('api:verify-email') + f'?token={verification.token}'
                            )
                            send_mail(
                                subject='Verify your email',
                                message=f'Click the link to verify your email: {verification_url}',
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[user.email],
                            )
                            return Response({'detail': 'A new verification link has been sent to your email.'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'detail': 'User with this email already exists and is active.'}, status=status.HTTP_400_BAD_REQUEST)
                    # If user does not exist, create new user
                    user = serializer.save()
                    expiry = timezone.now() + timedelta(minutes=10)
                    verification = EmailVerification.objects.create(user=user, expiry=expiry)
                    verification_url = request.build_absolute_uri(
                        reverse('api:verify-email') + f'?token={verification.token}'
                    )
                    send_mail(
                        subject='Verify your email',
                        message=f'Click the link to verify your email: {verification_url}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                    )
            except Exception as e:
                return Response({'detail': f'User registration failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'User registered. Please check your email to verify your account.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            verification = EmailVerification.objects.get(token=token)
        except EmailVerification.DoesNotExist:
            return Response({'detail': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)
        if verification.is_verified:
            return Response({'detail': 'Email already verified.'}, status=status.HTTP_200_OK)
        if verification.is_expired():
            # Resend new verification
            verification.token = uuid.uuid4()
            verification.expiry = timezone.now() + timedelta(minutes=10)
            verification.save()
            verification_url = request.build_absolute_uri(
                reverse('api:verify-email') + f'?token={verification.token}'
            )
            send_mail(
                subject='Verify your email',
                message=f'Click the link to verify your email: {verification_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[verification.user.email],
            )
            return Response({'detail': 'Verification link expired. A new link has been sent.'}, status=status.HTTP_400_BAD_REQUEST)
        # Mark as verified and activate user
        verification.is_verified = True
        verification.save()
        user = verification.user
        user.is_active = True
        user.save()
        return Response({'detail': 'Email verified. You can now log in.'}, status=status.HTTP_200_OK)
