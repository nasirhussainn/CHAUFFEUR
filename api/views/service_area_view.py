from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import ServiceArea
from api.serializers.service_area_serializer import ServiceAreaSerializer

class ServiceAreaViewSet(viewsets.ModelViewSet):
    queryset = ServiceArea.objects.all()
    serializer_class = ServiceAreaSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Service area created successfully.",
            "data": response.data
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Service area updated successfully.",
            "data": response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Service area deleted successfully.",
            
        }, status=status.HTTP_200_OK)
