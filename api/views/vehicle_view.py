from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models.vehicle import Vehicle, CarImage
from api.serializers.vehicle_serializer import VehicleSerializer
from rest_framework.decorators import action

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
        response = super().destroy(request, *args, **kwargs)
        return Response({
            "message": "Vehicle deleted successfully.",
        }, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['delete'], url_path='delete-images')
    def delete_images(self, request):
        image_ids = request.data.get('image_ids', [])
        if not isinstance(image_ids, list) or not image_ids:
            return Response({"error": "image_ids must be a non-empty list."}, status=400)

        deleted = 0
        not_found = []

        for image_id in image_ids:
            try:
                image = CarImage.objects.get(id=image_id)
                image.delete()  # Triggers your post_delete signal, deletes file and DB record
                deleted += 1
            except CarImage.DoesNotExist:
                not_found.append(image_id)

        return Response({
            "message": "Images deleted.",
            "deleted": deleted,
            "not_found": not_found
        }, status=200)