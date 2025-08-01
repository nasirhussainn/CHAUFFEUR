from rest_framework import serializers
from api.models.vehicle import Vehicle, CarImage, CarFeature
import json
from django.conf import settings

class VehicleSerializer(serializers.ModelSerializer):
    features = serializers.CharField(write_only=True, required=False)
    images = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)

    class Meta:
        model = Vehicle
        fields = [
            'id', 'type', 'model', 'price_per_mile', 'price_per_hour',
            'description', 'luggages', 'passengers', 'status', 'flat_rate',
            'features', 'images'
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        if request:
            scheme = request.scheme
            host = request.get_host().split(':')[0]

            if not settings.DEBUG:
                port = settings.CUSTOM_IMAGE_PORT
                base_url = f"{scheme}://{host}:{port}"
            else:
                base_url = request.build_absolute_uri('/')[:-1]

            rep['images'] = [
                {"id": img.id, "image": f"{base_url}{img.image.url}"}
                for img in instance.images.all()
            ]
        else:
            rep['images'] = []

        rep['features'] = [
            {"id": f.id, "feature": f.feature}
            for f in instance.features.all()
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
        features_raw = validated_data.pop('features', None)
        images = validated_data.pop('images', None)

        # Update only provided fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Add or replace features
        if features_raw is not None:
            try:
                features = json.loads(features_raw)
            except json.JSONDecodeError:
                raise serializers.ValidationError({"features": "Must be a valid JSON list of strings."})

            # Always replace features, even for PATCH
            instance.features.all().delete()

            # Add new features (avoid duplicates in input)
            added = set()
            for f in features:
                if f not in added:
                    CarFeature.objects.create(vehicle=instance, feature=f)
                    added.add(f)

        # Add new images (do not delete old ones)
        if images is not None:
            for img in images:
                CarImage.objects.create(vehicle=instance, image=img)

        return instance

