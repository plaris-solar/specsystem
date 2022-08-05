from rest_framework.exceptions import ValidationError
import sys, traceback
import sqlalchemy as sa
from rest_framework.permissions import BasePermission
from django.db import connection
from dateutil.parser import parse
import json

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


def get_db_host_name():
    server = DB_SETTINGS['HOST']
    if 'sqlexpress' in server:
        server = ".\sqlexpress"
    db = DB_SETTINGS['NAME']
    return server, db


def df_to_json_list(df):
    json_str_data = df.to_json(orient='records', lines=True).strip('\n').split('\n')
    json_data = [json.loads(d) for d in json_str_data]
    return json_data

def db_engine(server, db):
    connection_uri = sa.engine.url.URL(
        "mssql+pyodbc",
        host=server,
        database=db,  # required; not an empty string
        query={"driver": 'ODBC Driver 17 for SQL Server'},
    )
    return sa.create_engine(connection_uri)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def contains_bad_chars(str_val, bad_chars=None):
    if not bad_chars:
        bad_chars = BAD_CHARS
    return any(c in str_val for c in bad_chars)

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try:
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False
