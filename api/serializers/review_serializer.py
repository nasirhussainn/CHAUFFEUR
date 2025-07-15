from rest_framework import serializers
from api.models.review import Review
from api.models.booking import Booking

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'booking', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at', 'user']

    def validate_booking(self, value):
        request = self.context['request']
        user = request.user

        if value.user != user:
            raise serializers.ValidationError("You can only review your own bookings.")

        if value.status != 'completed':
            raise serializers.ValidationError("You can only review completed bookings.")

        # Only check for existing review on create
        if request.method == 'POST' and hasattr(value, 'review'):
            raise serializers.ValidationError("This booking has already been reviewed.")

        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
