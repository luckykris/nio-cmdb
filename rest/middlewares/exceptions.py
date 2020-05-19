from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class HandleExceptionMiddleware(MiddlewareMixin):

    def process_exception(self, request, exception):
        return JsonResponse({"detail": str(exception)}, status=500)