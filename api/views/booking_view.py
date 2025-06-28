from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from api.models import Booking
from api.serializers.booking_serializer import BookingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        queryset = Booking.objects.all()
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user=user_id)
        return queryset

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_booking(self, request, pk=None):
        booking = self.get_object()

        if timezone.now() > booking.created_at + timedelta(hours=24):
            return Response({
                "error": "Cancellation not allowed after 24 hours. 100% charge applies."
            }, status=status.HTTP_403_FORBIDDEN)

        booking.status = "canceled"
        booking.save()
        return Response({"message": "Booking has been successfully canceled."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='by-status')
    def bookings_by_status(self, request):
        status_param = request.query_params.get('status')
        user_id = request.query_params.get('user_id')

        if not status_param:
            return Response({"error": "Missing 'status' query parameter."}, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(status__iexact=status_param)
        if user_id:
            bookings = bookings.filter(user=user_id)

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
            return Response({"error": "Missing 'period' query parameter (week or month)."}, status=status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
        elif period == 'month':
            start_date = now - timedelta(days=30)
        else:
            return Response({"error": "Invalid period. Use 'week' or 'month'."}, status=status.HTTP_400_BAD_REQUEST)

        bookings = Booking.objects.filter(created_at__gte=start_date)
        if user_id:
            bookings = bookings.filter(user=user_id)

        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)