from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.vehicle_view import VehicleViewSet
from api.views.vehicle_detail_view import CarImageViewSet, CarFeatureViewSet
from api.views.landing import landing_view
from api.views.custom_upload import MultiImageUploadView

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'car-images', CarImageViewSet, basename='carimage')
router.register(r'car-features', CarFeatureViewSet, basename='carfeature')

urlpatterns = [
    path('', landing_view, name='landing'),
    path('car-images/multi-upload/', MultiImageUploadView.as_view(), name='multi-image-upload'),
    path('', include(router.urls)),
]
