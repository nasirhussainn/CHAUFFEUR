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
                            # Update user fields if changed
                            updated = False
                            for field in ['first_name', 'last_name', 'phone', 'gender']:
                                new_value = serializer.validated_data.get(field)
                                if new_value is not None and getattr(user, field) != new_value:
                                    setattr(user, field, new_value)
                                    updated = True
                            if updated:
                                user.save()
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
                            print("EMAIL_BACKEND:", settings.EMAIL_BACKEND)
                            print("EMAIL_HOST:", settings.EMAIL_HOST)
                            print("EMAIL_PORT:", settings.EMAIL_PORT)
                            print("EMAIL_HOST_USER:", settings.EMAIL_HOST_USER)
                            print("EMAIL_USE_SSL:", settings.EMAIL_USE_SSL)
                            print("DEFAULT_FROM_EMAIL:", settings.DEFAULT_FROM_EMAIL)
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

class UserRegistrationsByPeriodView(APIView):
    def get(self, request):
        period = request.query_params.get('period')
        if not period:
            return Response({'error': "Missing 'period' query parameter (week or month)."}, status=status.HTTP_400_BAD_REQUEST)
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            return Response({'error': "Invalid period. Use 'week' or 'month'."}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(date_joined__gte=start_date)
        user_data = [
            {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': getattr(user, 'phone', None),
                'gender': getattr(user, 'gender', None),
                'date_joined': user.date_joined,
            }
            for user in users
        ]
        return Response({'period': period, 'user_registrations': user_data})
