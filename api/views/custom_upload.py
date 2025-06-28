from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models.vehicle import CarImage, Vehicle
from django.shortcuts import get_object_or_404

class MultiImageUploadView(APIView):
    def post(self, request):
        vehicle_id = request.data.get('vehicle')
        images = request.FILES.getlist('images')

        if not vehicle_id or not images:
            return Response({
                "error": "Both 'vehicle' and at least one 'images' file are required."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Ensure vehicle exists
        vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

        uploaded = []
        for image in images:
            car_image = CarImage.objects.create(vehicle=vehicle, image=image)
            uploaded.append({
                "id": car_image.id,
                "image": request.build_absolute_uri(car_image.image.url)
            })

        return Response({
            "message": f"{len(uploaded)} image(s) uploaded successfully.",
            "uploaded": uploaded
        }, status=status.HTTP_201_CREATED)
