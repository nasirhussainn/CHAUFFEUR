from rest_framework import viewsets, status
from rest_framework.response import Response
from api.models import Contact
from api.serializers.contact_serializer import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "message": "Contact created successfully.",
            "data": response.data
        }, status=response.status_code)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "message": "Contact updated successfully.",
            "data": response.data
        }, status=response.status_code)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Contact deleted successfully.",
            
        }, status=status.HTTP_200_OK)

