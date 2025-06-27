from rest_framework import viewsets
from api.models.vehicle import CarImage, CarFeature
from api.serializers.vehicle_detail_serializer import CarImageSerializer, CarFeatureSerializer

class CarImageViewSet(viewsets.ModelViewSet):
    queryset = CarImage.objects.all()
    serializer_class = CarImageSerializer

class CarFeatureViewSet(viewsets.ModelViewSet):
    queryset = CarFeature.objects.all()
    serializer_class = CarFeatureSerializer
