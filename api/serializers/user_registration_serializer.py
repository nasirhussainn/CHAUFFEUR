from rest_framework import serializers
from django.contrib.auth import get_user_model
import re
import uuid
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()
    phone = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'first_name', 'last_name', 'phone', 'gender']

    def create(self, validated_data):
        while True:
            username = f"user_{uuid.uuid4().hex[:16]}"
            if not User.objects.filter(username=username).exists():
                break
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            gender=validated_data.get('gender', ''),
            is_active=False
        )
        return user

    def validate_phone(self, value):
        # Accepts only US phone numbers with +1 country code
        pattern = r'^\+1\s?([2-9][0-9]{2})[\s-]?[0-9]{3}[\s-]?[0-9]{4}$'
        if not re.match(pattern, value):
            raise serializers.ValidationError('Phone number must be a valid US number with +1 country code (e.g., +1 6191234567 or +1 503-123-4567).')
        return value
