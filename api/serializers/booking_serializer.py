from rest_framework import serializers
from django.core.validators import RegexValidator
from django.core.mail import send_mail
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from api.models import (
    Booking, Passenger, Stop, ChildSeat, PromoCode,
    Comment, FlightInformation
)

# -- Subserializers --

class PassengerSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        required=False,
        validators=[RegexValidator(
            regex=r'^\+1\s?\d{3}[\s\-]?\d{3}[\s\-]?\d{4}$',
            message="Phone number must be US format (e.g. +1 503-123-4567)"
        )]
    )

    class Meta:
        model = Passenger
        exclude = ['booking']

class StopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stop
        exclude = ['booking']

class ChildSeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildSeat
        exclude = ['booking']

class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        exclude = ['booking']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        exclude = ['booking']

class FlightInfoSerializer(serializers.ModelSerializer):
    meet_and_greet = serializers.BooleanField(required=False, default=False)

    class Meta:
        model = FlightInformation
        exclude = ['booking']

# -- Main Booking Serializer --

class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True)
    stops = StopSerializer(many=True, required=False)
    child_seats = ChildSeatSerializer(many=True, required=False)
    promo_code = PromoCodeSerializer(required=False)
    flight_info = FlightInfoSerializer(required=False)
    comments = CommentSerializer(many=True, required=False)

    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        type_of_ride = data.get('type_of_ride')
        flight_info = data.get('flight_info')

        if type_of_ride and type_of_ride.name.lower() != 'from airport' and flight_info:
            raise serializers.ValidationError({
                "flight_info": "Flight information is only allowed for 'from airport' bookings."
            })

        if type_of_ride and type_of_ride.name.lower() == 'from airport' and not flight_info:
            raise serializers.ValidationError({
                "flight_info": "Flight information is required for 'from airport' bookings."
            })

        return data

    def create(self, validated_data):
        passengers_data = validated_data.pop('passengers')
        stops_data = validated_data.pop('stops', [])
        child_seats_data = validated_data.pop('child_seats', [])
        promo_code_data = validated_data.pop('promo_code', None)
        flight_info_data = validated_data.pop('flight_info', None)
        comments_data = validated_data.pop('comments', [])

        # Calculate pricing
        base_price = Decimal(validated_data.get('price', 0))
        child_seat_fee = sum(
            Decimal("40.00") * Decimal(cs.get("quantity", 1)) for cs in child_seats_data
        )
        meet_greet = flight_info_data.get('meet_and_greet') if isinstance(flight_info_data, dict) else False
        meet_greet_fee = Decimal("50.00") if meet_greet else Decimal("0.00")
        subtotal = base_price + child_seat_fee + meet_greet_fee
        total_price = subtotal * Decimal("1.20")
        validated_data['price'] = total_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        booking = Booking.objects.create(**validated_data)

        # Save nested records
        for p in passengers_data:
            Passenger.objects.create(booking=booking, **p)
        for s in stops_data:
            Stop.objects.create(booking=booking, **s)
        for seat in child_seats_data:
            ChildSeat.objects.create(booking=booking, **seat)
        for c in comments_data:
            Comment.objects.create(booking=booking, **c)
        if promo_code_data:
            PromoCode.objects.create(booking=booking, **promo_code_data)
        if isinstance(flight_info_data, dict) and flight_info_data:
            FlightInformation.objects.create(booking=booking, **flight_info_data)

        return booking

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'canceled':
            if instance.created_at and instance.created_at < timezone.now() - timezone.timedelta(hours=24):
                raise serializers.ValidationError({
                    "status": "Cannot cancel after 24 hours. Full charge applies."
                })

        passengers_data = validated_data.pop('passengers', [])
        stops_data = validated_data.pop('stops', [])
        child_seats_data = validated_data.pop('child_seats', [])
        promo_code_data = validated_data.pop('promo_code', None)
        flight_info_data = validated_data.pop('flight_info', None)
        comments_data = validated_data.pop('comments', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.passengers.all().delete()
        for p in passengers_data:
            Passenger.objects.create(booking=instance, **p)

        instance.stops.all().delete()
        for s in stops_data:
            Stop.objects.create(booking=instance, **s)

        instance.child_seats.all().delete()
        for seat in child_seats_data:
            ChildSeat.objects.create(booking=instance, **seat)

        instance.comments.all().delete()
        for c in comments_data:
            Comment.objects.create(booking=instance, **c)

        if promo_code_data:
            PromoCode.objects.update_or_create(booking=instance, defaults=promo_code_data)
        if flight_info_data:
            FlightInformation.objects.update_or_create(booking=instance, defaults=flight_info_data)

        return instance
