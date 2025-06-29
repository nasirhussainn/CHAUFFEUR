from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import Service
from api.serializers.service_serializer import ServiceSerializer

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Service created successfully.",
            "data": response.data
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Service updated successfully.",
            "data": response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Service deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)
