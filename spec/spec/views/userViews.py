import re
from django.contrib.auth.models import User as DjangoUser
from django.db import transaction
from proj.util import IsSuperUserOrReadOnly
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from spec.serializers.userSerializers import UserSerializer, UserUpdateSerializer
from utils.dev_utils import formatError

from user.models import User
from ..models import  Role, RoleUser
from ..serializers.roleSerializers import RoleSerializer, RolePostSerializer, RoleUpdateSerializer

class UserList(GenericAPIView):
    """ 
    get:
    Return list of users
    """
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = DjangoUser.objects.all()
    search_fields = ('username', 'first_name', 'last_name', )

    def get(self, request, format=None):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = self.paginate_queryset(queryset.order_by('username'))
            
            serializer = UserSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U01")


class UserDetail(APIView):
    """
    get:
    user/<username>
    Return details of specific user

    put:
    user/<username>
    Update <user> with new delegates

    {
        "delegates": "user1, user3"
    }
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_object(self, username):
        try:
            return DjangoUser.objects.get(username=username)
        except DjangoUser.DoesNotExist:
            raise ValidationError({"errorCode":"SPEC-U02", "error": f"User ({username}) does not exist."})

    def get(self, request, username, format=None):
        try:
            username = self.get_object(username)
            serializer = UserSerializer(username)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U03")

    def put(self, request, username, format=None):
        try:
            with transaction.atomic():
                username = self.get_object(username)
                serializer = UserUpdateSerializer(username, data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-U04", "error": "Invalid message format", "schemaErrors":serializer.errors})
                serializer.save()
            serializer = UserSerializer(username)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U05")
