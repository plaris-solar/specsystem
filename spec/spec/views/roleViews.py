import re
from django.db import transaction
from proj.util import IsSuperUserOrReadOnly
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from utils.dev_utils import formatError

from user.models import User
from ..models import  Role, RoleUser
from ..serializers.roleSerializers import RoleSerializer, RolePostSerializer, RoleUpdateSerializer

class RoleList(GenericAPIView):
    """ 
    get:
    Return list of roles

    post:
    Create role

    {
        "role": "DOC_MGR",
        "descr": "Document control manager",
        "spec_one": true,
        "users": "user1, user2"
    }
    """
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    search_fields = ('role','descr')

    def get(self, request, format=None):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = self.paginate_queryset(queryset.order_by('role'))
            
            serializer = RoleSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V01")

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                if re.search(r'[^-a-zA-Z0-9_]+',request.data["role"]):
                    raise ValidationError({"errorCode":"SPEC-V17", "error": "Role names cannot contain special characters, including: space, comma, tab, semicolon and colon"})
                serializer = RolePostSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V02", "error": "Invalid message format", "schemaErrors":serializer.errors})
                role = serializer.save()
            serializer = RoleSerializer(role)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V03")


class RoleDetail(APIView):
    """
    get:
    role/<role>
    Return details of specific role

    put:
    role/<role>
    Update <role> with new description or users

    {
        "descr": "Document control manager",
        "spec_one": true,
        "users": "user1, user3"
    }

    delete:
    role/<role>
    Delete specified <role> entry
    """
    permission_classes = [IsSuperUserOrReadOnly]
    def get_object(self, role):
        try:
            return Role.objects.get(role=role)
        except Role.DoesNotExist:
            raise ValidationError({"errorCode":"SPEC-V04", "error": f"Role ({role}) does not exist."})

    def get(self, request, role, format=None):
        try:
            role = self.get_object(role)
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V05")

    def put(self, request, role, format=None):
        try:
            with transaction.atomic():
                role = self.get_object(role)
                serializer = RoleUpdateSerializer(role, data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V06", "error": "Invalid message format", "schemaErrors":serializer.errors})
                serializer.save()
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V07")

    def delete(self, request, role, format=None):
        try:
            with transaction.atomic():
                role = self.get_object(role)
                role.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V08")
