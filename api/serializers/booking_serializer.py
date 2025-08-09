from rest_framework import serializers
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from api.models import (
    Booking, Passenger, Stop, ChildSeat, PromoCode,
    Comment, FlightInformation, TaxRate
)
from api.serializers.payment_serializer import PaymentSerializer
from .user_serializer import UserSerializer
from api.serializers.review_serializer import ReviewSerializer

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
    user = UserSerializer(read_only=True)
    passengers = PassengerSerializer(many=True)
    stops = StopSerializer(many=True, required=False)
    child_seats = ChildSeatSerializer(many=True, required=False)
    promo_code = serializers.SerializerMethodField()
    flight_info = FlightInfoSerializer(required=False)
    comments = CommentSerializer(many=True, required=False)
    payment = serializers.SerializerMethodField()
    review = ReviewSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'

    def get_promo_code(self, obj):
        if hasattr(obj, 'promo_code_obj'):
            return obj.promo_code_obj.promo_code
        return None

    def get_payment(self, obj):
        from api.models import Payment
        try:
            payment = Payment.objects.get(booking=obj)
            return PaymentSerializer(payment).data
        except Payment.DoesNotExist:
            return None

    def validate(self, data):
        type_of_ride = data.get('type_of_ride', '').lower()
        flight_info = data.get('flight_info')

        ALLOWED_RIDES = [
            'from-airport', 'to-airport', 'point-to-point', 'hourly-as-directed',
            'wine-tour', 'tour', 'prom', 'weddings'
        ]

        if type_of_ride not in ALLOWED_RIDES:
            raise serializers.ValidationError({
                "type_of_ride": f"Invalid ride type. Must be one of: {', '.join(ALLOWED_RIDES)}"
            })

        if type_of_ride != 'from-airport' and flight_info:
            raise serializers.ValidationError({
                "flight_info": "Flight information is only allowed for 'from-airport' bookings."
            })

        if type_of_ride == 'from-airport' and not flight_info:
            raise serializers.ValidationError({
                "flight_info": "Flight information is required for 'from-airport' bookings."
            })

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data.pop('user', None)
        user = request.user if request and request.user.is_authenticated else None
        validated_data['user'] = user

        passengers_data = validated_data.pop('passengers')
        stops_data = validated_data.pop('stops', [])
        child_seats_data = validated_data.pop('child_seats', [])
        flight_info_data = validated_data.pop('flight_info', None)
        comments_data = validated_data.pop('comments', [])

        promo_code_data = request.data.get('promo_code') if request else None

        base_price = Decimal(validated_data.get('price', 0))
        child_seat_fee = sum(
            Decimal("20.00") * Decimal(cs.get("quantity", 1)) for cs in child_seats_data
        )
        meet_greet = flight_info_data.get('meet_and_greet') if isinstance(flight_info_data, dict) else False
        meet_greet_fee = Decimal("40.00") if meet_greet else Decimal("0.00")
        stop_fee = Decimal("25.00") * Decimal(len(stops_data))

        subtotal = base_price + child_seat_fee + meet_greet_fee + stop_fee

        # --- Discount logic
        is_discounted = False
        if user and not user.new_user_discount_used:
            subtotal *= Decimal("0.90")  # 10% discount
            is_discounted = True

        # --- Service fee
        with_service_fee = subtotal * Decimal("1.20")

        # --- Tax
        try:
            tax_record = TaxRate.objects.first()
            tax_percentage = tax_record.rate_percentage if tax_record else Decimal("0.00")
        except TaxRate.DoesNotExist:
            tax_percentage = Decimal("0.00")

        tax_amount = with_service_fee * (tax_percentage / Decimal("100.00"))
        final_price = with_service_fee + tax_amount

        validated_data['price'] = final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        validated_data['is_discounted'] = is_discounted

        # --- Create Booking
        booking = Booking.objects.create(**validated_data)

        for p in passengers_data:
            Passenger.objects.create(booking=booking, **p)
        for s in stops_data:
            Stop.objects.create(booking=booking, **s)
        for seat in child_seats_data:
            ChildSeat.objects.create(booking=booking, **seat)
        for c in comments_data:
            Comment.objects.create(booking=booking, **c)
        if promo_code_data:
            PromoCode.objects.create(booking=booking, promo_code=promo_code_data)
        if isinstance(flight_info_data, dict) and flight_info_data:
            FlightInformation.objects.create(booking=booking, **flight_info_data)

        if user and is_discounted:
            user.new_user_discount_used = True
            user.save()

        return booking

    def update(self, instance, validated_data):
        if validated_data.get('status') == 'canceled':
            if instance.created_at and instance.created_at < timezone.now() - timezone.timedelta(hours=24):
                raise serializers.ValidationError({
                    "status": "Cannot cancel after 24 hours. Full charge applies."
                })

        request = self.context.get('request')
        is_partial = request and request.method == 'PATCH'

        passengers_data = validated_data.pop('passengers', None)
        stops_data = validated_data.pop('stops', None)
        child_seats_data = validated_data.pop('child_seats', None)
        promo_code_data = request.data.get('promo_code') if request else None
        flight_info_data = validated_data.pop('flight_info', None)
        comments_data = validated_data.pop('comments', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if passengers_data is not None:
            if not is_partial:
                instance.passengers.all().delete()
            for p in passengers_data:
                Passenger.objects.create(booking=instance, **p)

        if stops_data is not None:
            if not is_partial:
                instance.stops.all().delete()
            for s in stops_data:
                Stop.objects.create(booking=instance, **s)

        if child_seats_data is not None:
            instance.child_seats.all().delete()
            for seat in child_seats_data:
                ChildSeat.objects.create(booking=instance, **seat)

        if comments_data is not None:
            if not is_partial:
                instance.comments.all().delete()
            for c in comments_data:
                Comment.objects.create(booking=instance, **c)

        if promo_code_data:
            PromoCode.objects.update_or_create(
                booking=instance,
                defaults={"promo_code": promo_code_data}
            )

        if flight_info_data is not None:
            if hasattr(instance, 'flight_info'):
                instance.flight_info.delete()
            FlightInformation.objects.create(booking=instance, **flight_info_data)

        # --- Price recalculation when relevant data changes
        if child_seats_data is not None or flight_info_data is not None or stops_data is not None:
            base_price = Decimal(instance.price or 0)
            child_seat_fee = sum(
                Decimal("40.00") * Decimal(seat.get("quantity", 1)) for seat in (child_seats_data or [])
            )

            meet_greet = False
            if flight_info_data and isinstance(flight_info_data, dict):
                meet_greet = flight_info_data.get("meet_and_greet", False)
            elif hasattr(instance, 'flight_info'):
                meet_greet = instance.flight_info.meet_and_greet

            meet_greet_fee = Decimal("50.00") if meet_greet else Decimal("0.00")
            stop_fee = Decimal("25.00") * Decimal(len(stops_data or instance.stops.all()))

            subtotal = base_price + child_seat_fee + meet_greet_fee + stop_fee

            # NEW USER DISCOUNT LOGIC
            user = instance.user
            is_discounted = False
            if hasattr(user, 'new_user_discount_used') and not user.new_user_discount_used:
                discount_amount = subtotal * Decimal("0.10")
                subtotal -= discount_amount
                instance.is_discounted = True
                user.new_user_discount_used = True
                user.save()
                is_discounted = True
            else:
                instance.is_discounted = False

            with_service_fee = subtotal * Decimal("1.20")

            try:
                tax_record = TaxRate.objects.first()
                tax_percentage = tax_record.rate_percentage if tax_record else Decimal("0.00")
            except TaxRate.DoesNotExist:
                tax_percentage = Decimal("0.00")

            tax_amount = with_service_fee * (tax_percentage / Decimal("100.00"))
            final_price = with_service_fee + tax_amount

            instance.price = final_price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            instance.save()

        return instance
