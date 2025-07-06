from rest_framework import serializers
from api.models.payment import Payment
from api.models.booking import Booking

class PaymentSerializer(serializers.ModelSerializer):
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking'
    )
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Payment
        fields = ['booking_id', 'total_cost', 'payment_method', 'transaction_id', 'payment_status', 'paid_at']
        read_only_fields = ['payment_method', 'transaction_id', 'payment_status', 'paid_at']
