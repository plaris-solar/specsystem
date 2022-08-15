import re
from django.db import transaction
from proj.util import IsSuperUserOrReadOnly
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from utils.dev_utils import formatError

from ..models import  DocType
from ..serializers.docTypeSerializers import DocTypeSerializer, DocTypePutSerializer

class DocTypeList(GenericAPIView):
    """ 
    get:
    Return list of DocTypes

    post:
    Create DocType

    {
        "name": "WI",
        "descr": "Work Instruction",
        "confidential": false
    }
    """
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = DocType.objects.all()
    serializer_class = DocTypeSerializer
    search_fields = ('name','descr')

    def get(self, request, format=None):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = self.paginate_queryset(queryset.order_by('name'))
            
            serializer = DocTypeSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-DTV01")

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                if re.search('[\s|\,|\t|\;|/]+',request.data["name"]):
                    raise ValidationError({"errorCode":"SPEC-V17", "error": "Doc Type names cannot contain special characters, including: space, comma, tab, semicolon and slash"})
                serializer = DocTypeSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-DTV03", "error": "Invalid message format", "schemaErrors":serializer.errors})
                doctype = serializer.save()
            serializer = DocTypeSerializer(doctype)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-DTV04")


class DocTypeDetail(APIView):
    """
    get:
    doctype/<doctype>
    Return details of specific DocType

    put:
    doctype/<doctype>
    Update <doctype> 

    {
        "name": "WI",
        "descr": "Work Instruction",
        "confidential": false
    }

    delete:
    doctype/<doctype>
    Delete specified <doctype> entry
    """
    permission_classes = [IsSuperUserOrReadOnly]
    def get_object(self, doctype):
        try:
            return DocType.objects.get(name=doctype)
        except DocType.DoesNotExist:
            raise ValidationError({"errorCode":"SPEC-DTV05", "error": f"DocType ({doctype}) does not exist."})

    def get(self, request, doctype, format=None):
        try:
            doctype = self.get_object(doctype)
            serializer = DocTypeSerializer(doctype)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-DTV06")

    def put(self, request, doctype, format=None):
        try:
            with transaction.atomic():
                doctype = self.get_object(doctype)
                serializer = DocTypePutSerializer(doctype, data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-DTV07", "error": "Invalid message format", "schemaErrors":serializer.errors})
                doctype = serializer.save()
            serializer = DocTypeSerializer(doctype)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-DTV08")

    def delete(self, request, doctype, format=None):
        try:
            with transaction.atomic():
                doctype = self.get_object(doctype)
                doctype.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-DTV09")