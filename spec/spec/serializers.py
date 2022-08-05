import re
from user.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, CategoryReadRole, CategorySignRole, Role, RoleUser

class RoleSerializer(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True)
    class Meta:
        model = Role
        fields = ('role', 'descr', 'any', 'active', 'users', )

    def to_representation(self, value):
        data = super(RoleSerializer, self).to_representation(value)
        data['users'] = ', '.join(data['users'])
        return data

class RolePostSerializer(serializers.ModelSerializer):
    users = serializers.CharField(required=False, default=None, allow_null=True)
    class Meta:
        model = Role
        fields = ('role', 'descr', 'any', 'active', 'users', )
    
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
    descr = serializers.CharField(allow_null=True)
    any = serializers.BooleanField()
    active = serializers.BooleanField()
    users = serializers.CharField(required=False, default=None, allow_blank=True)

class CategorySerializer(serializers.ModelSerializer):
    signRoles = serializers.StringRelatedField(many=True)
    readRoles = serializers.StringRelatedField(many=True)
    class Meta:
        model = Category
        fields = ('cat', 'sub_cat', 'descr', 'active', 'confidential', 'jira_temp', 'signRoles', 'readRoles', )

    def to_representation(self, value):
        data = super(CategorySerializer, self).to_representation(value)
        data['signRoles'] = ', '.join(data['signRoles'])
        data['readRoles'] = ', '.join(data['readRoles'])
        return data

class CategoryPostSerializer(serializers.ModelSerializer):
    signRoles = serializers.CharField(required=False, default=None, allow_blank=True)
    readRoles = serializers.CharField(required=False, default=None, allow_blank=True)
    class Meta:
        model = Category
        fields = ('cat', 'sub_cat', 'descr', 'active', 'confidential', 'jira_temp', 'signRoles', 'readRoles',  )
    
    def create(self, validated_data):
        sign_role_data = validated_data.pop("signRoles")
        read_role_data = validated_data.pop("readRoles")
        category = Category.objects.create(**validated_data)

        if sign_role_data:
            roles = re.split('[\s|\,|\t|\;|\:]+',sign_role_data)
            for role in roles:
                _role = Role.lookup(role)
                _signRole = CategorySignRole.objects.create(cat=category,role=_role)

        if read_role_data:
            roles = re.split('[\s|\,|\t|\;|\:]+',read_role_data)
            for role in roles:
                _role = Role.lookup(role)
                _readRole = CategoryReadRole.objects.create(cat=category,role=_role)

        return category

class CategoryUpdateSerializer(serializers.Serializer):
    cat = serializers.CharField(required=False)
    sub_cat = serializers.CharField(required=False)
    descr = serializers.CharField()
    active = serializers.BooleanField()
    confidential = serializers.BooleanField()
    jira_temp = serializers.CharField(required=False, default=None, allow_blank=True)
    signRoles = serializers.CharField(required=False, default=None, allow_blank=True)
    readRoles = serializers.CharField(required=False, default=None, allow_blank=True)


