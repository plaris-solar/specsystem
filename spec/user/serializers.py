
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .authentication import expires_in, is_token_expired

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token

    def to_representation(self, instance):
        data = {
            "user": instance.user.username,
            "created": instance.created,
            "expires_in": str(expires_in(instance)),
            "expired": is_token_expired(instance),
            "admin": instance.user.is_superuser,
            "read_all": instance.user.is_staff,
            "active": instance.user.is_active,
        }
        return data