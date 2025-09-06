from django_filters.rest_framework import DjangoFilterBackend
from api.models.quote_request import QuoteRequest
from api.serializers.quote_request_serializer import QuoteRequestSerializer, QuoteRequestStatusSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


class QuoteRequestCreateView(generics.CreateAPIView):
    queryset = QuoteRequest.objects.all()
    serializer_class = QuoteRequestSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            quote = serializer.save(user=self.request.user)
        else:
            quote = serializer.save()

        # send emails after save
        self._send_admin_email(quote)
        self._send_user_email(quote)

    def _send_admin_email(self, quote):
        subject = f"📌 New Quote Request #{quote.reference}"
        html = render_to_string("emails/quote_admin_email.html", {
            "reference": quote.reference,
            "status": quote.status,
            "vehicle": quote.vehicle,
            "first_name": quote.first_name if not quote.user else quote.user.first_name,
            "last_name": quote.last_name if not quote.user else quote.user.last_name,
            "email": quote.email if not quote.user else quote.user.email,
            "phone": quote.phone if not quote.user else quote.user.profile.phone if hasattr(quote.user, "profile") else None,
        })
        email = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_RECEIVER_EMAIL])
        email.content_subtype = "html"
        email.send()

    def _send_user_email(self, quote):
        subject = f"Your Quote Request #{quote.reference}"
        html = render_to_string("emails/quote_user_email.html", {
            "reference": quote.reference,
            "status": quote.status,
            "vehicle": quote.vehicle,
            "first_name": quote.first_name if not quote.user else quote.user.first_name,
            "last_name": quote.last_name if not quote.user else quote.user.last_name,
        })
        recipient = quote.email if not quote.user else quote.user.email
        email = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, [recipient])
        email.content_subtype = "html"
        email.send()


class QuoteRequestListView(generics.ListAPIView):
    queryset = QuoteRequest.objects.all().order_by("-created_at")
    serializer_class = QuoteRequestSerializer
    # 🌍 Public access
    permission_classes = [permissions.AllowAny]

    # ✅ Enable filtering
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "vehicle", "email", "reference"]


class QuoteRequestDetailView(generics.RetrieveUpdateAPIView):
    queryset = QuoteRequest.objects.all()
    permission_classes = [permissions.AllowAny]  # 🔓 Public for dev

    def get_serializer_class(self):
        # For PATCH requests, only allow status updates
        if self.request.method in ["PUT", "PATCH"]:
            return QuoteRequestStatusSerializer
        return QuoteRequestSerializer
