from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.vehicle_view import VehicleViewSet
from api.views.vehicle_detail_view import CarImageViewSet, CarFeatureViewSet
from api.views.landing import landing_view
from api.views.custom_upload import MultiImageUploadView
from api.views.user_registration_view import UserRegistrationView, VerifyEmailView
from api.views.user_login_view import UserLoginView
from api.views.password_reset_request_view import PasswordResetRequestView
from api.views.password_reset_confirm_view import PasswordResetConfirmView
from api.views.admin_user_list_view import AdminUserListView

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'car-images', CarImageViewSet, basename='carimage')
router.register(r'car-features', CarFeatureViewSet, basename='carfeature')

urlpatterns = [
    path('', landing_view, name='landing'),
    path('car-images/multi-upload/', MultiImageUploadView.as_view(), name='multi-image-upload'),
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('', include(router.urls)),
]
