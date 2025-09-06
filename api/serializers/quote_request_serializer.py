from rest_framework import serializers
from api.models.quote_request import QuoteRequest

class QuoteRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = [
            "id", "reference", "vehicle", "user",
            "first_name", "last_name", "email", "phone",
            "status", "created_at"
        ]
        read_only_fields = ["id", "reference", "status", "created_at", "user"]
    def validate(self, data):
        user = self.context["request"].user

        if not user.is_authenticated:
            # Guest must provide email and first_name
            if not data.get("email"):
                raise serializers.ValidationError({"email": "Guest must provide an email."})
            if not data.get("first_name"):
                raise serializers.ValidationError({"first_name": "Guest must provide a first name."})

        return data

class QuoteRequestStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = ["status"]  