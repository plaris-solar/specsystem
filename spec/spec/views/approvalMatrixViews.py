import re
from django.db import transaction
from proj.util import IsSuperUserOrReadOnly
from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from utils.dev_utils import formatError

from ..models import ApprovalMatrix, ApprovalMatrixSignRole, DepartmentReadRole, Role
from ..serializers.approvalMatrixSerializers import ApprovalMatrixSerializer, ApprovalMatrixPostSerializer, ApprovalMatrixUpdateSerializer

class ApprovalMatrixList(GenericAPIView):
    """ 
    get:
    approvalmatrix/
    Return list of Approval Matricies

    post:
    Create ApprovalMatrix

    {
        "doc_type": "Requirement",
        "dept": "IT",
        "signRoles": "ITMgr"
    }
    """
    permission_classes = [IsSuperUserOrReadOnly]
    queryset = ApprovalMatrix.objects.all()
    serializer_class = ApprovalMatrixSerializer
    search_fields = ('doc_type__name','department__name')

    def get(self, request, format=None):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            queryset = self.paginate_queryset(queryset.order_by('doc_type__name','department__name'))
            
            serializer = ApprovalMatrixSerializer(queryset, many=True)
            return self.get_paginated_response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V09")

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                serializer = ApprovalMatrixPostSerializer(data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V10", "error": "Invalid message format", "schemaErrors":serializer.errors})
                ApprovalMatrix = serializer.save()
            serializer = ApprovalMatrixSerializer(ApprovalMatrix)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V11")


class ApprovalMatrixDetail(APIView):
    """
    get:
    approvalmatrix/<cat>/<sub_cat>
    Return details of specific ApprovalMatrix / sub-ApprovalMatrix

    put:
    approvalmatrix/<cat>/<sub_cat>
    Update ApprovalMatrix / sub-ApprovalMatrix with new description or roles

    {
        "doc_type": "Requirement",
        "dept": "IT",
        "signRoles": "ITMgr"
    }

    delete:
    approvalmatrix/<cat>/<sub_cat>
    Delete specified ApprovalMatrix / sub-ApprovalMatrix entry
    """
    permission_classes = [IsSuperUserOrReadOnly]
    def get_object(self, id):
        try:
            return ApprovalMatrix.objects.get(id=id)
        except ApprovalMatrix.DoesNotExist:
            raise ValidationError({"errorCode":"SPEC-V12", "error": f"ApprovalMatrix ({id}) does not exist."})

    def get(self, request, id, format=None):
        try:
            apvl_mt = self.get_object(id)
            serializer = ApprovalMatrixSerializer(apvl_mt)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V13")

    def put(self, request, id, format=None):
        try:
            with transaction.atomic():
                apvl_mt = self.get_object(id)
                serializer = ApprovalMatrixUpdateSerializer(apvl_mt, data=request.data)
                if not serializer.is_valid():
                    raise ValidationError({"errorCode":"SPEC-V14", "error": "Invalid message format", "schemaErrors":serializer.errors})
                apvl_mt = serializer.save()
            serializer = ApprovalMatrixSerializer(apvl_mt)
            return Response(serializer.data)
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-V15")

    def delete(self, request, id, format=None):
        try:
            with transaction.atomic():
                apvl_mt = self.get_object(id)
                apvl_mt.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except BaseException as be: # pragma: no cover
            formatError(be, "SPEC-DPV8")
