from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from api.models.contact_message import ContactMessage
from api.serializers.contact_message_serializer import ContactMessageSerializer

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def perform_create(self, serializer):
        contact = serializer.save()

        # --- Admin Email ---
        admin_subject = "New Contact Message"
        admin_html = render_to_string("emails/contact_email.html", {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "message": contact.message
        })
        admin_email = EmailMessage(
            subject=admin_subject,
            body=admin_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_RECEIVER_EMAIL]
        )
        admin_email.content_subtype = "html"
        admin_email.send()

        # --- User Confirmation Email ---
        user_subject = "We Received Your Message"
        user_html = render_to_string("emails/contact_confirmation_email.html", {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "message": contact.message
        })
        user_email = EmailMessage(
            subject=user_subject,
            body=user_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[contact.email]
        )
        user_email.content_subtype = "html"
        user_email.send()

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Contact message deleted successfully.",
        }, status=status.HTTP_200_OK)
