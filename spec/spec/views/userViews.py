import re
from django.contrib.auth.models import User as DjangoUser
from django.db import transaction
from proj.util import IsSuperUserOrReadOnly
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from spec.models import Spec, UserWatch
from spec.serializers.userSerializers import UserSerializer, UserUpdateSerializer
from user.models import User
from utils.dev_utils import formatError

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
    def get(self, request, username, format=None):
        try:
            username = User.lookup(username)
            serializer = UserSerializer(username)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U02")

    def put(self, request, username, format=None):
        try:
            with transaction.atomic():
                username = User.lookup(username)
                serializer = UserUpdateSerializer(username, data=request.data)
                if not serializer.is_valid(): # pragma nocover
                    raise ValidationError({"errorCode":"SPEC-U03", "error": "Invalid message format", "schemaErrors":serializer.errors})
                serializer.save()
            serializer = UserSerializer(username)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U04")


class UserWatchView(APIView):
    """
    post:
    user/watch/<username>/<spec_num>
    Add spec_num to user's watch list

    delete:
    user/watch/<username>/<spec_num>
    Remove spec_num from user's watch list    
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    @staticmethod
    def auth_check(request, username):
        if not request.user.is_superuser and request.user.username != username:
            raise ValidationError({"errorCode":"SPEC-U05", "error": f"Only admins can change other's settings."})

    def post(self, request, username, spec_num, format=None):
        try:
            with transaction.atomic():
                UserWatchView.auth_check(request, username)

                spec_num = int(spec_num)
                user = User.lookup(username)
                specFound = Spec.objects.filter(num=spec_num).count()
                if specFound == 0:
                    raise ValidationError({"errorCode":"SPEC-U06", "error": f"Spec {spec_num} does not exist."})
                # Delete to prevent error on duplicate entry
                UserWatch.objects.filter(user=user, num=spec_num).delete()
                UserWatch.objects.create(user=user, num=spec_num)

            serializer = UserSerializer(user)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U07")

    def delete(self, request, username, spec_num, format=None):
        try:
            with transaction.atomic():
                UserWatchView.auth_check(request, username)
                spec_num = int(spec_num)
                user = User.lookup(username)
                UserWatch.objects.filter(user=user, num=spec_num).delete()

            serializer = UserSerializer(user)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-U08")
