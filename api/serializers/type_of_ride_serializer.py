from rest_framework import serializers
from api.models import TypeOfRide

class TypeOfRideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeOfRide
        fields = '__all__'
