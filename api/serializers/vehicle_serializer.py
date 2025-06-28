from rest_framework import serializers
from api.models.vehicle import Vehicle, CarImage, CarFeature
import json

class VehicleSerializer(serializers.ModelSerializer):
    features = serializers.CharField(write_only=True)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'type', 'model', 'price_per_mile', 'price_per_hour',
            'description', 'luggages', 'passengers', 'status',
            'features', 'images'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['features'] = [
            {"id": f.id, "feature": f.feature}
            for f in instance.features.all()
        ]
        rep['images'] = [
            {"id": img.id, "image": self.context['request'].build_absolute_uri(img.image.url)}
            for img in instance.images.all()
        ]
        return rep

    def create(self, validated_data):
        features_raw = validated_data.pop('features', '[]')
        images = validated_data.pop('images', [])

        try:
            features = json.loads(features_raw)
        except json.JSONDecodeError:
            raise serializers.ValidationError({"features": "Must be a valid JSON list of strings."})

        vehicle = Vehicle.objects.create(**validated_data)

        for f in features:
            CarFeature.objects.create(vehicle=vehicle, feature=f)

        for img in images:
            CarImage.objects.create(vehicle=vehicle, image=img)

        return vehicle

    def update(self, instance, validated_data):
        features_raw = validated_data.pop('features', '[]')
        images = validated_data.pop('images', [])

        try:
            features = json.loads(features_raw)
        except json.JSONDecodeError:
            raise serializers.ValidationError({"features": "Must be a valid JSON list of strings."})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if features:
            instance.features.all().delete()
            for f in features:
                CarFeature.objects.create(vehicle=instance, feature=f)

        if images:
            instance.images.all().delete()
            for img in images:
                CarImage.objects.create(vehicle=instance, image=img)

        return instance
