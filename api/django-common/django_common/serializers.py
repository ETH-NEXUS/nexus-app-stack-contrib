from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "email", "is_superuser", "groups")
