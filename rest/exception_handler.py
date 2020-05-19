from rest_framework.views import exception_handler
from rest_framework.response import Response
from traceback import format_exc
import re


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is None:
        status,  detail = my_handler_exception(exc)
        data = {'status_code': status, 'detail': detail}
        response = Response(data, status=status)
    return response


def my_handler_exception(exc):
    s = 500
    d = format_exc()
    p = "1062, \"Duplicate entry (?P<dr>'.+?') for key"
    ret = re.search(p, str(exc))
    r = ret.group('dr')
    if r:
        l = r.split('-')
        if len(l) > 1:
            r = "-".join(l[1:])
        s = 409
        d = 'duplicate value: \'' + r
    return s, d
