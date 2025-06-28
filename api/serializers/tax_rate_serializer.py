from rest_framework import serializers
from api.models import TaxRate

class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'
