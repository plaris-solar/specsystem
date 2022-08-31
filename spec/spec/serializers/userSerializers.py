import re
from user.models import User
from rest_framework import serializers

from ..models import Role, RoleUser, UserDelegate

class UserSerializer(serializers.ModelSerializer):
    delegates = serializers.StringRelatedField(many=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'email', 'delegates' )

    def to_representation(self, value):
        data = super(UserSerializer, self).to_representation(value)
        data['delegates'] = ', '.join(sorted(data['delegates']))
        return data

class UserUpdateSerializer(serializers.Serializer):
    delegates = serializers.CharField(required=False, default=None, allow_blank=True, allow_null=True)
    
    def update(self, user, validated_data):
        UserDelegate.objects.filter(user=user).delete()           
        if validated_data["delegates"]:         
            delegates = re.split(r"[\s:;,]+", validated_data["delegates"])
            for delegate in delegates:
                if len(delegate) > 0:
                    d = User.lookup(username=delegate)
                    user_delegate = UserDelegate.objects.create(user=user, delegate=d)

        return user


