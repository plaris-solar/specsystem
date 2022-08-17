from rest_framework.exceptions import ValidationError
import sys, traceback
from rest_framework.permissions import BasePermission
from django.db import connection

DB_SETTINGS = connection.settings_dict
BAD_CHARS = [',', ';', ' ']

META_SCHEMA = {'lot_id*': 'string', 'row_num': 'number', 'creation_tm': 'string', 'doc_type': 'string'}


def formatError(exc, defaultCode):
    """
    Handle all error returns from views.
    If the exception is already a ValidationError, add traceback information and pass it on.
    For other exceptions, create a ValidationError with our standard fields.
    """
    if isinstance(exc, ValidationError):
        exc.detail['traceBack'] = f"File: {sys.exc_info()[2].tb_frame.f_code.co_filename} Line: {sys.exc_info()[2].tb_lineno} Function: {sys.exc_info()[2].tb_frame.f_code.co_name}"
        raise
    else: # pragma no cover
        raise ValidationError({"errorCode":defaultCode, "error":sys.exc_info()[1], "traceBack":traceback.format_exc()})


class IsSuperUser(BasePermission):
    """
    Allows access only to super users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)
