import re
from user.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Category, CategoryReadRole, CategorySignRole, Role, RoleUser, Spec, SpecFile, SpecHist, SpecReference, SpecSig

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

class SpecSigSerializer(serializers.ModelSerializer):
    signer = serializers.CharField(source='signer.__str__')
    delegate = serializers.CharField(source='delegate.__str__')
    class Meta:
        model = SpecSig
        fields = ('role', 'signer', 'delegate', 'signed_dt', 'from_cat', )

    def to_representation(self, value):
        data = super(SpecSigSerializer, self).to_representation(value)
        if "__str__" in data['signer']:
            data['signer'] = None
        if "__str__" in data['delegate']:
            data['delegate'] = None
        return data

class SpecHistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecHist
        fields = ('mod_ts', 'upd_by', 'change_type', 'comment', )

class SpecFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecFile
        fields = ('seq', '_filename', )

class SpecReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecReference
        fields = ('num', 'ver', )

class SpecSerializer(serializers.ModelSerializer):
    cat = serializers.CharField(source='cat.__str__')
    sigs = SpecSigSerializer(many=True)
    hist = SpecHistSerializer(many=True)
    files = SpecFileSerializer(many=True)
    refs = SpecReferenceSerializer(many=True)
    class Meta:
        model = Spec
        fields = ('num', 'ver', 'title', 'keywords', 'state', 'cat', 'create_dt', 'mod_ts', 'sigs', 'hist', 'files', 'refs', )
        
class SpecSigPostSerializer(serializers.Serializer):
    role = serializers.CharField()
    signer = serializers.CharField(required=False, default=None, allow_null=True)
    from_cat = serializers.BooleanField(required=False, default=False)
        
class SpecFilePostSerializer(serializers.Serializer):
    _filename = serializers.CharField()

class SpecPostSerializer(serializers.Serializer):
    title = serializers.CharField()
    keywords = serializers.CharField(required=False, default=None, allow_blank=True)
    cat = serializers.CharField()
    sigs = SpecSigPostSerializer(many=True)
    files = SpecFilePostSerializer(many=True)
    refs = SpecReferenceSerializer(many=True)

