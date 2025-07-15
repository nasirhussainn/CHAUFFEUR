from rest_framework import viewsets, permissions
from api.models.review import Review
from api.serializers.review_serializer import ReviewSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a review to edit/delete it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_queryset(self):
        # Filter to only show reviews belonging to the current user
        return Review.objects.filter(user=self.request.user)
