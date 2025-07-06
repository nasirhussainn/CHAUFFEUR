import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import Booking, Payment
from django.utils import timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

class CreateStripeIntentView(APIView):
    def post(self, request):
        booking_id = request.data.get("bookingId")
        booking = Booking.objects.filter(id=booking_id).first()
        if not booking:
            return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

        amount = int(booking.price * 100)  # convert to cents

        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="usd",
                automatic_payment_methods={"enabled": True},
                metadata={"booking_id": str(booking.id)}
            )
            return Response({"client_secret": intent.client_secret}, status=200)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)

class ConfirmPaymentView(APIView):
    def post(self, request, booking_id):
        data = request.data

        # Validate expected fields
        required_keys = ['id', 'payment_method', 'amount', 'status']
        for key in required_keys:
            if key not in data:
                return Response({'error': f'Missing field: {key}'}, status=status.HTTP_400_BAD_REQUEST)

        if data['status'] != 'succeeded':
            return Response({'error': 'Payment status is not succeeded'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Retrieve full payment method details from Stripe
            payment_method = stripe.PaymentMethod.retrieve(data['payment_method'])
            card_info = payment_method.get("card", {})
            card_brand = card_info.get("brand", "unknown")
            last4 = card_info.get("last4", "")
        except Exception as e:
            return Response({'error': f'Failed to retrieve payment method: {str(e)}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Save payment details
        Payment.objects.update_or_create(
            booking=booking,
            defaults={
                "payment_method": card_brand,
                "transaction_id": data['id'],
                "total_cost": data['amount'] / 100,  # Convert from cents
                "payment_status": True,
                "paid_at": timezone.now(),
            }
        )

        # Update booking status
        booking.payment_status = True
        booking.save()

        return Response({'message': 'Payment confirmed and saved.'}, status=status.HTTP_200_OK)