from django.db import transaction
from django.http import FileResponse
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from spec.services.spec_create import specCreate, specRevise
from ..services.spec_route import specReject, specSign, specSubmit
from spec.services.spec_update import specFileUpload, specUpdate
from utils.dev_utils import formatError

from ..models import Spec, SpecFile
from ..serializers.specSerializers import FilePostSerializer, SpecPostSerializer, SpecRejectSerializer, SpecSerializer, SpecSignSerializer

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
        "doc_type": "Requirement",
        "department": "IT",
        "keywords": "SPEC",
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
            queryset = self.queryset
            queryset = queryset.filter(num = request.GET.get('num')) if request.GET.get('num') else queryset
            queryset = queryset.filter(title__contains = request.GET.get('title')) if request.GET.get('title') else queryset
            queryset = queryset.filter(keywords__contains = request.GET.get('keywords')) if request.GET.get('keywords') else queryset
            queryset = queryset.filter(state__contains = request.GET.get('state')) if request.GET.get('state') else queryset
            queryset = queryset.filter(created_by__contains = request.GET.get('created_by')) if request.GET.get('created_by') else queryset

            if num is not None:
                queryset = queryset.filter(num=num)
            
            if not request.GET.get('incl_obsolete'):                
                queryset = queryset.exclude(state='Obsolete')
            queryset = self.paginate_queryset(queryset.order_by('num', 'ver'))
            
            serializer = SpecSerializer(queryset, many=True, context={'user':request.user})
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
            serializer = SpecSerializer(spec, context={'user':request.user})
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
        "state": "Draft",
        "title": "REQ, SPEC SYSTEM",
        "keywords": "SPEC",
        "cat": "IT",
        "sub_cat": "Requirement",
        "sigs": [{"role": "ITMgr", "signer": "ahawse"}],
        "files": [{"filename": "Req.docx", "seq": 1}],
        "refs": [{"num": 300000, "ver": "A"}],
        "comment": "Changes made today"
    }

    post:
    spec/<num>/<ver>
    Create a new revision of the spec

    delete:
    spec/<num>/<ver>
    Delete specified spec entry
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, num, ver, format=None):
        try:
            spec = Spec.lookup(int(num), ver, request.user)
            serializer = SpecSerializer(spec, context={'user':request.user})
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
            serializer = SpecSerializer(spec, context={'user':request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V30")

    def post(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                spec = specRevise(request, spec)
            serializer = SpecSerializer(spec, context={'user':request.user})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V24")

    def delete(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                spec.checkEditable(request.user)
                spec.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V24")


class SpecFileDetail(APIView):
    """
    get:
    file/<num>/<ver>/<fileName>
    Return details of specific file

    post:
    file/<num>/<ver>
    Uploads a file to spec

    {
        "file": {
            "name":"Inv.docx",
            "file":<_io.BytesIO object>
        }
    }

    delete:
    file/<num>/<ver>/<fileName>
    Delete file from spec 
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, num, ver="*", fileName=None, format=None):
        try:
            specFile = SpecFile.lookup(num, ver, fileName, request.user)
            osFileName = specFile.file.path
            response = FileResponse(open(osFileName, 'rb'), filename=specFile.filename)
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
            serializer = SpecSerializer(spec, context={'user':request.user})
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


class SpecSubmit(APIView):
    """
    post:
    spec/submit/<num>/<ver>
    Submit spec for signatures

    {
    }
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                spec = specSubmit(request, spec)
            serializer = SpecSerializer(spec, context={'user':request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V25")


class SpecSign(APIView):
    """
    post:
    spec/sign/<num>/<ver>
    Sign spec

    {
        "role":"ITMgr",
        "signer":"ahawse"
    }
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                serializer = SpecSignSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V29", "error": "Invalid message format", "schemaErrors":serializer.errors})
                spec = specSign(request, spec, serializer.validated_data)
            serializer = SpecSerializer(spec, context={'user':request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V26")



class SpecReject(APIView):
    """
    post:
    spec/reject/<num>/<ver>
    Reject spec send back to Draft

    {
    }
    """
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, num, ver, format=None):
        try:
            with transaction.atomic():
                spec = Spec.lookup(num, ver, request.user)
                serializer = SpecRejectSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V27", "error": "Invalid message format", "schemaErrors":serializer.errors})
                spec = specReject(request, spec, serializer.validated_data)
            serializer = SpecSerializer(spec, context={'user':request.user})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V28")

