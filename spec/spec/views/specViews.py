from django.db import transaction
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from spec.services.spec_create import specCreate
from spec.services.spec_update import specFileUpload, specUpdate
from utils.dev_utils import formatError

from ..models import Spec, SpecFile
from ..serializers.specSerializers import FilePostSerializer, SpecPostSerializer, SpecSerializer

class SpecList(GenericAPIView):
    """ 
    get:
    spec/
    spec/<num>
    Return list of specs

    post:
    Create spec

    {
        "title": "REQ, SPEC SYSTEM",
        "keywords": "SPEC",
        "cat": "IT",
        "sub_cat": "Requirement",
        "sigs": [{"role": "ITMgr", "signer": "ahawse"}],
        "files": [{"filename": "Req.docx", "seq": 1}],
        "refs": [{"num": 300000, "ver": "A"}]
    }
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Spec.objects.all()
    serializer_class = SpecSerializer
    search_fields = ('title','keywords')

    def get(self, request, num=None, format=None):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if num is not None:
                queryset = queryset.filter(num=num)
            queryset = self.paginate_queryset(queryset.order_by('num', 'ver'))
            
            serializer = SpecSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V17")

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = SpecPostSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V18", "error": "Invalid message format", "schemaErrors":serializer.errors})
                spec = specCreate(request, serializer.validated_data)
            serializer = SpecSerializer(spec)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V19")


class SpecDetail(APIView):
    """
    get:
    spec/<num>/<ver>
    Return details of specific Spec

    put:
    spec/<num>/<ver>
    Update spec

    {
        "title": "REQ, SPEC SYSTEM",
        "keywords": "SPEC",
        "cat": "IT",
        "sub_cat": "Requirement",
        "sigs": [{"role": "ITMgr", "signer": "ahawse"}],
        "files": [{"filename": "Req.docx", "seq": 1}],
        "refs": [{"num": 300000, "ver": "A"}]
    }

    delete:
    spec/<num>/<ver>
    Delete specified spec entry
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, num, ver, format=None):
        try:
            spec = Spec.lookup(num, ver, request.user)
            serializer = SpecSerializer(spec)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V21")

    def put(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                serializer = SpecPostSerializer(spec, data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V22", "error": "Invalid message format", "schemaErrors":serializer.errors})
                spec = specUpdate(request, spec, serializer.validated_data)
            serializer = SpecSerializer(spec)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V23")

    def delete(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                cat = Spec.lookup(num, ver, request.user)
                cat.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V24")


class SpecFileDetail(APIView):
    """
    get:
    spec/file/<num>/<ver>/<fileName>
    Return details of specific file

    post:
    spec/<num>/<ver>
    Uploads a file to spec

    {
        "title": "REQ, SPEC SYSTEM",
        "keywords": "SPEC",
        "cat": "IT",
        "sub_cat": "Requirement",
        "sigs": [{"role": "ITMgr", "signer": "ahawse"}],
        "files": [{"filename": "Req.docx", "seq": 1}],
        "refs": [{"num": 300000, "ver": "A"}]
    }

    delete:
    spec/<num>/<ver>/<fileName>
    Delete file from spec 
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, num, ver, fileName, format=None):
        try:
            specFile = SpecFile.lookup(num, ver, fileName, request.user)
            osFileName = specFile.file.path
            response = FileResponse(open(osFileName, 'rb'))
            return response
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V21")

    def post(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                spec.checkEditable(request.user)
                serializer = FilePostSerializer(spec, data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V22", "error": "Invalid message format", "schemaErrors":serializer.errors})
                spec = specFileUpload(request, spec, serializer.validated_data)
            serializer = SpecSerializer(spec)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V23")

    def delete(self, request, num, ver, fileName, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                spec.checkEditable(request.user)
                SpecFile.objects.filter(spec=spec, filename=fileName).delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V24")
