from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from api.models import Booking
from api.serializers.booking_serializer import BookingSerializer
from rest_framework.permissions import IsAuthenticated
from api.pagination import DynamicPageNumberPagination

class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = DynamicPageNumberPagination

    def get_queryset(self):
        queryset = Booking.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user=user_id)
        return queryset

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()
        user = request.user

        # If user is not admin, check cancellation window
        if not (user.is_staff or user.is_superuser):
            vehicle_type = getattr(booking.vehicle, 'type', '').lower()
            if vehicle_type == 'sprinter-van':
                if timezone.now() > booking.created_at + timedelta(hours=72):
                    return Response({
                        "message": "Cancellation for Sprinter Van bookings not allowed after 72 hours. 100% charge applies."
                    }, status=status.HTTP_403_FORBIDDEN)
            else:
                if timezone.now() > booking.created_at + timedelta(hours=24):
                    return Response({
                        "message": "Cancellation not allowed after 24 hours. 100% charge applies."
                    }, status=status.HTTP_403_FORBIDDEN)

        booking.status = "canceled"
        booking.save()
        return Response({
            "message": "Booking has been successfully canceled."
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='by-status')
    def bookings_by_status(self, request):
        status_param = request.query_params.get('status')
        user_id = request.query_params.get('user_id')
        payment_status = request.query_params.get('payment_status')

        if not status_param:
            return Response({
                "message": "Missing 'status' query parameter."
            }, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(status__iexact=status_param)

        if user_id:
            bookings = bookings.filter(user=user_id)

        if payment_status is not None:
            if payment_status.lower() in ['true', '1']:
                bookings = bookings.filter(payment_status=True)
            elif payment_status.lower() in ['false', '0']:
                bookings = bookings.filter(payment_status=False)

        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    
    @action(detail=False, methods=['get'], url_path='by-period')
    def bookings_by_period(self, request):
        period = request.query_params.get('period')
        user_id = request.query_params.get('user_id')

        if not period:
            return Response({
                "message": "Missing 'period' query parameter (week or month)."
            }, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            return Response({
                "message": "Invalid period. Use 'week' or 'month'."
            }, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(created_at__gte=start_date)
        if user_id:
            bookings = bookings.filter(user=user_id)

        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='confirm')
    def confirm_booking(self, request, pk=None):
        booking = self.get_object()
        user = request.user
        # confirm_param = request.query_params.get('confirm', 'false').lower()
        # confirm_flag = confirm_param == 'true'

        if not (user.is_staff or user.is_superuser):
            return Response({
                "message": "Only admins can confirm bookings."
            }, status=status.HTTP_403_FORBIDDEN)

        if booking.status != 'pending':
            return Response({
                "message": "Only pending bookings can be confirmed."
            }, status=status.HTTP_400_BAD_REQUEST)

        # if not booking.payment_status:
        #     if not confirm_flag:
        #         return Response({
        #             "message": "Warning: You are about to confirm a booking without completed payment. Please confirm to proceed."
        #         }, status=status.HTTP_400_BAD_REQUEST)
        # If confirm=true or payment is done, proceed
        booking.status = "confirmed"
        booking.save()
        return Response({
            "message": "Booking has been confirmed successfully."
        }, status=status.HTTP_200_OK)

    
    @action(detail=True, methods=['post'], url_path='complete') 
    def complete_booking(self, request, pk=None):
        booking = self.get_object()

        if booking.status != 'confirmed':
            return Response({
                "message": "Only confirmed bookings can be marked as completed."
            }, status=status.HTTP_400_BAD_REQUEST)

        booking.status = "completed"
        booking.save()
        return Response({
            "message": "Booking has been marked as completed successfully."
        }, status=status.HTTP_200_OK)