from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.vehicle_view import VehicleViewSet
from api.views.landing import landing_view
from api.views.booking_view import BookingViewSet
from api.views.type_of_ride_view import TypeOfRideViewSet
from api.views.service_view import ServiceViewSet
from api.views.service_area_view import ServiceAreaViewSet
from api.views.tax_rate_view import TaxRateViewSet

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'type-of-ride', TypeOfRideViewSet, basename='type-of-ride')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'service-areas', ServiceAreaViewSet, basename='service-areas')
router.register(r'tax-rates', TaxRateViewSet, basename='tax-rates')

urlpatterns = [
    path('', landing_view, name='landing'),
    path('', include(router.urls)),
]
