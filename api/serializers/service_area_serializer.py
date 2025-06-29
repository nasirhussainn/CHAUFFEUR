from rest_framework import serializers
from api.models import ServiceArea
from django.conf import settings

class ServiceAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceArea
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')

        def build_url(image_field):
            if not image_field:
                return None
            if request:
                scheme = request.scheme
                host = request.get_host().split(':')[0]
                if not settings.DEBUG:
                    port = getattr(settings, 'CUSTOM_IMAGE_PORT', '8080')
                    base_url = f"{scheme}://{host}:{port}"
                else:
                    base_url = request.build_absolute_uri('/')[:-1]
                return f"{base_url}{image_field.url}"
            return image_field.url

        rep['image1'] = build_url(instance.image1)
        rep['image2'] = build_url(instance.image2)
        return rep
