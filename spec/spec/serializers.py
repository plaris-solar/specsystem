import re
from user.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, CategoryRole, Role, RoleUser

class RoleSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True)
    class Meta:
        model = Role
        fields = ('role', 'descr', 'any', 'users', )

    def to_representation(self, value):
        data = super(RoleSerializer, self).to_representation(value)
        data['users'] = ', '.join(data['users'])
        return data

class RolePostSerializer(serializers.ModelSerializer):
    users = serializers.CharField(required=False, default=None, allow_null=True)
    class Meta:
        model = Role
        fields = ('role', 'descr', 'any', 'users', )
    
    def create(self, validated_data):
        role_user_data = validated_data.pop("users")
        role = Role.objects.create(**validated_data)
        if role_user_data:
            users = re.split('[\s|\,|\t|\;|\:]+',role_user_data)
            for role_user in users:
                user = User.lookup(username=role_user)
                role_user = RoleUser.objects.create(role=role,user=user)
        return role

class RoleUpdateSerializer(serializers.Serializer):
    descr = serializers.CharField(required=False, default=None)
    any = serializers.BooleanField(required=False, default=None)
    users = serializers.CharField(required=False, default=None, allow_null=True)

class CategorySerializer(serializers.ModelSerializer):
    roles = serializers.StringRelatedField(many=True)
    class Meta:
        model = Category
        fields = ('cat', 'sub_cat', 'descr', 'active', 'confidential', 'file_temp', 'jira_temp', 'roles', )

    def to_representation(self, value):
        data = super(CategorySerializer, self).to_representation(value)
        data['roles'] = ', '.join(data['roles'])
        return data

class CategoryPostSerializer(serializers.ModelSerializer):
    roles = serializers.CharField(required=False, default=None, allow_null=True)
    class Meta:
        model = Category
        fields = ('cat', 'sub_cat', 'descr', 'active', 'confidential', 'file_temp', 'jira_temp', 'roles', )
    
    def create(self, validated_data):
        category_role_data = validated_data.pop("roles")
        category = Category.objects.create(**validated_data)
        if category_role_data:
            category_roles = re.split('[\s|\,|\t|\;|\:]+',category_role_data)
            for category_role in category_roles:
                role = Role.objects.filter(role=category_role).first()
                if not role:
                    raise ValidationError({"errorCode":"SPEC-S01", "error": f"Role ({category_role}) does not exist."})
                category_role = CategoryRole.objects.create(cat=category,role=role)
        return category

class CategoryUpdateSerializer(serializers.Serializer):
    cat = serializers.CharField(required=False, default=None)
    sub_cat = serializers.CharField(required=False, default=None)
    descr = serializers.CharField(required=False, default=None)
    active = serializers.BooleanField(required=False, default=None)
    confidential = serializers.BooleanField(required=False, default=None)
    file_temp = serializers.CharField(required=False, default=None)
    jira_temp = serializers.CharField(required=False, default=None)
    roles = serializers.CharField(required=False, default=None, allow_null=True)


