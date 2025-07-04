from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import TypeOfRide
from api.serializers.type_of_ride_serializer import TypeOfRideSerializer
from api.pagination import DynamicPageNumberPagination
class TypeOfRideViewSet(viewsets.ModelViewSet):
    queryset = TypeOfRide.objects.all()
    serializer_class = TypeOfRideSerializer
    pagination_class = DynamicPageNumberPagination
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Type of ride created successfully.",
            "data": response.data
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Type of ride updated successfully.",
            "data": response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Type of ride deleted successfully.", 
        }, status=status.HTTP_200_OK)

