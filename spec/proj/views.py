from rest_framework.decorators import APIView
from django.db import connection
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from proj.util import IsSuperUser
import os
from utils.dev_utils import formatError


class QaDbReset(APIView):

    permission_classes = [IsSuperUser]

    def delete(self, request, format=None): # pragma no cover
        cursor = connection.cursor()
        dbName = connection.settings_dict['NAME']
        if 'qa' not in dbName:
            raise ValidationError({"errorCode":"FLU-001", "error": f"Can only apply this function to a database with 'qa' in the name. Current database {dbName} does not."})

        cursor.execute("TRUNCATE TABLE data_collection")
        cursor.execute("TRUNCATE TABLE data_hist")
        cursor.execute("TRUNCATE TABLE doc_type")
        cursor.execute("TRUNCATE TABLE doc_type_hist")

        return Response(status=status.HTTP_204_NO_CONTENT)


class Env(APIView):

    def get(self, request, format=None):
        try:
            return Response(os.getenv('AD_SUFFIX', 'Prod'))
        except BaseException as be: # pragma: no cover
            formatError(be, "ENV-001")