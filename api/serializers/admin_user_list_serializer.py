from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Exclude sensitive fields like password, last_login, etc.
        exclude = ['password', 'user_permissions', 'groups']
