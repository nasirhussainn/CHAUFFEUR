from rest_framework import viewsets
from api.models.vehicle import Vehicle
from api.serializers.vehicle_serializer import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
