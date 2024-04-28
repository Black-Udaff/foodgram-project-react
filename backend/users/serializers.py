from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = get_user_model()
        fields = ("id",
                  "email",
                  "username",
                  "first_name",
                  "last_name",
                  "password")
