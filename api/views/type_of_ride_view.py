from rest_framework import viewsets
from api.models import TypeOfRide
from api.serializers.type_of_ride_serializer import TypeOfRideSerializer

class TypeOfRideViewSet(viewsets.ModelViewSet):
    queryset = TypeOfRide.objects.all()
    serializer_class = TypeOfRideSerializer
