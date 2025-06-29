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
import traceback
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from utils.url_helpers import build_full_url

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
                            path = reverse('api:verify-email') + f'?token={verification.token}'
                            verification_url = build_full_url(request, path)
                            subject = 'Verify your email'
                            from_email = settings.DEFAULT_FROM_EMAIL
                            to_email = [user.email]
                            context = {'user': user, 'verification_url': verification_url}

                            text_content = f"Hi {user.first_name or 'User'},\n\nPlease verify your email:\n{verification_url}\n\nThanks,\nTeam"
                            html_content = render_to_string('emails/verify_email.html', context)

                            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                            email.attach_alternative(html_content, "text/html")
                            email.send()
                            return Response({'detail': 'A new verification link has been sent to your email.'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'detail': 'User with this email already exists and is active.'}, status=status.HTTP_400_BAD_REQUEST)
                    # If user does not exist, create new user
                    user = serializer.save()
                    expiry = timezone.now() + timedelta(minutes=10)
                    verification = EmailVerification.objects.create(user=user, expiry=expiry)
                    path = reverse('api:verify-email') + f'?token={verification.token}'
                    verification_url = build_full_url(request, path)

                    subject = 'Verify your email'
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_email = [user.email]
                    context = {'user': user, 'verification_url': verification_url}

                    text_content = f"Hi {user.first_name or 'User'},\n\nPlease verify your email:\n{verification_url}\n\nThanks,\nTeam"
                    html_content = render_to_string('emails/verify_email.html', context)

                    email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
                    email.attach_alternative(html_content, "text/html")
                    email.send()
            except Exception as e:
                traceback.print_exc()  
                return Response({'detail': f'User registration failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
            path = reverse('api:verify-email') + f'?token={verification.token}'
            verification_url = build_full_url(request, path)
            subject = 'Verify your email'
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [verification.user.email]
            context = {
                'user': verification.user,
                'verification_url': verification_url,
            }

            text_content = f"Hi {verification.user.first_name or 'User'},\n\nPlease verify your email by clicking the following link:\n{verification_url}\n\nThanks,\nTeam"
            html_content = render_to_string('emails/verify_email.html', context)

            email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            email.attach_alternative(html_content, "text/html")
            email.send()
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
