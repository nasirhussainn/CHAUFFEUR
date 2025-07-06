import stripe
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models.booking import Booking
from api.models.payment import Payment
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY  # Set this in settings.py

class CreatePaymentIntentView(APIView):
    def post(self, request):
        booking_id = request.data.get('bookingId')
        amount = request.data.get('amount')

        if not booking_id or not amount:
            return Response({'error': 'bookingId and amount are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Create or update Payment record
            payment, created = Payment.objects.get_or_create(booking=booking)
            payment.total_cost = amount
            payment.save()

            # Create Stripe PaymentIntent (amount in cents)
            intent = stripe.PaymentIntent.create(
                amount=int(float(amount) * 100),
                currency='usd',
                metadata={'booking_id': booking_id},
            )

            return Response({'client_secret': intent.client_secret}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
