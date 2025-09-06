from rest_framework.routers import DefaultRouter
from django.urls import path, include
from api.views.vehicle_view import VehicleViewSet
from api.views.user_registration_view import UserRegistrationView, VerifyEmailView, UserRegistrationsByPeriodView
from api.views.user_login_view import UserLoginView, MostRecentLoginsView
from api.views.password_reset_request_view import PasswordResetRequestView
from api.views.password_reset_confirm_view import PasswordResetConfirmView
from api.views.admin_user_list_view import AdminUserListView
from api.views.booking_view import BookingViewSet
from api.views.service_view import ServiceViewSet
from api.views.service_area_view import ServiceAreaViewSet
from api.views.tax_rate_view import TaxRateViewSet
from api.views.contact_view import ContactViewSet
from api.views.user_me_view import UserMeView
from api.views.logout_view import LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from api.views.payment_view import CreateStripeIntentView, ConfirmPaymentView
from api.views.contact_message_view import ContactMessageViewSet
from api.views.review_view import ReviewViewSet
from api.views.review_view import TopReviewsView
from api.views.quote_request_view import QuoteRequestCreateView, QuoteRequestDetailView, QuoteRequestListView

router = DefaultRouter()
router.register(r'vehicles', VehicleViewSet, basename='vehicle')
router.register(r'bookings', BookingViewSet, basename='booking')
router.register(r'services', ServiceViewSet, basename='services')
router.register(r'service-areas', ServiceAreaViewSet, basename='service-areas')
router.register(r'tax-rates', TaxRateViewSet, basename='tax-rates')
router.register(r'contacts', ContactViewSet, basename='contacts')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'contact-us', ContactMessageViewSet, basename='contact-us')

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('auth/login/', UserLoginView.as_view(), name='user-login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('admin/users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('analytics/most-recent-logins/', MostRecentLoginsView.as_view(), name='most-recent-logins'),
    path('analytics/user-registrations-by-period/', UserRegistrationsByPeriodView.as_view(), name='user-registrations-by-period'),
    path('user/me/', UserMeView.as_view(), name='user-me'),
    path('user/logout/', LogoutView.as_view(), name='user-logout'),
    
    path('stripe/create-intent/', CreateStripeIntentView.as_view(), name='create-stripe-intent'),
    path('bookings/<int:booking_id>/payment-confirmed/', ConfirmPaymentView.as_view()),
    
    path('reviews/top/', TopReviewsView.as_view(), name='top-reviews'), 
    
    path("quotes/create/", QuoteRequestCreateView.as_view(), name="quote-create"),
    path("quotes/", QuoteRequestListView.as_view(), name="quote-list"),
    path("quotes/<int:pk>/", QuoteRequestDetailView.as_view(), name="quote-detail"),
    
    path('', include(router.urls)),
]
