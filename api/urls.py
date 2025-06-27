from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.vehicle_view import VehicleViewSet
from api.views.vehicle_detail_view import CarImageViewSet, CarFeatureViewSet
from api.views.landing import landing_view

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'car-images', CarImageViewSet, basename='carimage')
router.register(r'car-features', CarFeatureViewSet, basename='carfeature')

urlpatterns = [
    path('', landing_view, name='landing'),
    path('', include(router.urls)),
]
