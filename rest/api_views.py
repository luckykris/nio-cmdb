from rest_framework.response import Response
from rest_framework.views import APIView
from .models import resource


class AttributeTypesApi(APIView):

    def get(self, request):
        for x in resource.AttributeDefined.__subclasses__():
            print(hasattr(x, 'relate'))
        attribute_types = [{'name':  x.__name__, 'relate': hasattr(x, 'relate')} for x in resource.AttributeDefined.__subclasses__()]

        return Response(attribute_types)
