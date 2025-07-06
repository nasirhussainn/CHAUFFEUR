# serializers/payment_serializer.py
from rest_framework import serializers
from api.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['payment_method', 'transaction_id', 'total_cost', 'payment_status', 'paid_at']
