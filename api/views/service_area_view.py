from rest_framework import viewsets
from api.models import ServiceArea
from api.serializers.service_area_serializer import ServiceAreaSerializer

class ServiceAreaViewSet(viewsets.ModelViewSet):
    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer
