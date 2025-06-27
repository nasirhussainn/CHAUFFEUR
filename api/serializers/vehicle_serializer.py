from rest_framework import serializers
from api.models.vehicle import Vehicle, CarImage, CarFeature

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'image']

class CarFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFeature
        fields = ['id', 'feature']

class VehicleSerializer(serializers.ModelSerializer):
    images = CarImageSerializer(many=True, read_only=True)
    features = CarFeatureSerializer(many=True, read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'type', 'model', 'price_per_mile', 'price_per_hour',
            'description', 'luggages', 'passengers', 'status',
            'images', 'features'  # 👈 include related objects
        ]
