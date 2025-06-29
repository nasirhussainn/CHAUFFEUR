from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models.vehicle import Vehicle
from api.serializers.vehicle_serializer import VehicleSerializer

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.prefetch_related('images', 'features').all()
    serializer_class = VehicleSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Vehicle created successfully.",
            "data": response.data
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Vehicle updated successfully.",
            "data": response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Vehicle deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)