from rest_framework import viewsets
from api.models import TaxRate
from api.serializers.tax_rate_serializer import TaxRateSerializer

class TaxRateViewSet(viewsets.ModelViewSet):
    queryset = TaxRate.objects.all()
    serializer_class = TaxRateSerializer
