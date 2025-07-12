from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from api.serializers.contact_message_serializer import ContactMessageSerializer
from django.conf import settings

class ContactMessageView(APIView):
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
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
                admin_subject,
                admin_html,
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_RECEIVER_EMAIL]
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
                user_subject,
                user_html,
                settings.DEFAULT_FROM_EMAIL,
                [contact.email]
            )
            user_email.content_subtype = "html"
            user_email.send()

            return Response({"message": "Your message has been sent successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
