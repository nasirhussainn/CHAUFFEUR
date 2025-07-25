from rest_framework import viewsets, permissions, generics
from api.models.review import Review
from api.serializers.review_serializer import ReviewSerializer, PublicReviewSerializer

# Custom permission
class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:  # Admin override
            return True
        return obj.user == request.user  # Normal users must own the review

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Review.objects.all()
        return Review.objects.filter(user=user)

class TopReviewsView(generics.ListAPIView):
    serializer_class = PublicReviewSerializer
    permission_classes = [permissions.AllowAny]  # Public access

    def get_queryset(self):
        return Review.objects.order_by('-rating', '-created_at')[:10]
