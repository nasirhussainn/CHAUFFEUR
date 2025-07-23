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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact = serializer.save()

        # Send emails
        self._send_admin_email(contact)
        self._send_user_email(contact)

        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Your message has been received successfully.",
            "data": response.data
        }, status=response.status_code)

    def _send_admin_email(self, contact):
        subject = "New Contact Message"
        html = render_to_string("emails/contact_email.html", {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "email": contact.email,
            "phone": contact.phone,
            "message": contact.message
        })
        email = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, [settings.CONTACT_RECEIVER_EMAIL])
        email.content_subtype = "html"
        email.send()

    def _send_user_email(self, contact):
        subject = "We Received Your Message"
        html = render_to_string("emails/contact_confirmation_email.html", {
            "first_name": contact.first_name,
            "last_name": contact.last_name,
            "message": contact.message
        })
        email = EmailMessage(subject, html, settings.DEFAULT_FROM_EMAIL, [contact.email])
        email.content_subtype = "html"
        email.send()

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "success": True,
            "message": "Contact message deleted successfully."
        }, status=status.HTTP_200_OK)
