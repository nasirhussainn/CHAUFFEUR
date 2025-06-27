from rest_framework import serializers
from api.models.vehicle import CarImage, CarFeature

class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['id', 'vehicle', 'image']

class CarFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarFeature
        fields = ['id', 'vehicle', 'feature']
