from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.filters import BaseFilterBackend, OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .models import Department, User
from . import serializers


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer

    @action(methods=['get'], detail=True)
    def expend_department_nodes(self, request, *args, **kwargs):
        u = self.get_object()
        serializer_context = {
            'request': request,
        }
        serializer = serializers.DepartmentSerializer(u.expend_department_nodes(), context=serializer_context, many=True)
        return Response(serializer.data)


# Create your views here.
class DepartmentViewSet(viewsets.ModelViewSet):
    # authentication_classes = (authentication.JWTAuthentication,)
    # permission_classes = (permissions.IsAuthenticated,)
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Department.objects.all()
    serializer_class = serializers.DepartmentSerializer


# class LabelViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = resource.Label.objects.all()
#     serializer_class = serializers.LabelSerializer


class AttributeDefinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = resource.AttributeDefined.objects.all()
    serializer_class = serializers.AttributeDefinedSerializer


class ResourceDefinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = resource.ResourceDefined.objects.all()
    serializer_class = serializers.ResourceDefinedSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = resource.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer


# class ResourceViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = resource.Resource.objects
#     serializer_class = serializers.ResourceSerializer


# class ResourceViewSet1(viewsets.ViewSet):
#     @staticmethod
#     def get_attribute_classname_by_attributeDefined(x):
#         return x[:-7]
#
#     def list(self, request, resourceDefined):
#         try:
#             rd = resource.ResourceDefined.objects.get(name=resourceDefined)
#         except resource.ResourceDefined.DoesNotExist:
#             raise exceptions.NotFound
#         attr_map = {x.id: x.name for x in rd.attributes.all()}
#         queryset = resource.Resource.objects.filter(type=rd)
#         serializer = serializers.ResourceSerializer(queryset, many=True, attr_map=attr_map)
#         return Response(serializer.data)
#
#     def create(self, request, resourceDefined):
#         try:
#             rd = resource.ResourceDefined.objects.get(name=resourceDefined)
#         except resource.ResourceDefined.DoesNotExist:
#             raise exceptions.NotFound
#         attr_map = {x.name: (x.id, ResourceViewSet.get_attribute_classname_by_attributeDefined(x.__class__.__name__)) for x in rd.attributes.all()}
#         serializer = serializers.ResourceSerializer(data=request.data, attr_map=attr_map, resourceDefined=rd)
#         serializer.is_valid(raise_exception=True)
#         r = serializer.create(serializer.validated_data)
#         return Response({"uuid": r.pk})


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = resource.Resource.objects.prefetch_related('departments', 'labels', 'attributes')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filter_fields = ('name', 'departments__name', 'labels__k', 'labels__v')
    search_fields = ('$name', '$departments__name', '$labels__k', 'labels__v',)
    ordering_fields = ('name', '_ctime', '_mtime')

    @staticmethod
    def get_attribute_classname_by_attributeDefined(x):
        return x[:-7]

    def get_serializer_class(self):
        sc = getattr(self, 'my_sc', None)
        if sc is None:
            resourceDefined = self.kwargs.get('resourceDefined')
            try:
                rd = resource.ResourceDefined.objects.prefetch_related('attributes').get(name=resourceDefined)
            except resource.ResourceDefined.DoesNotExist:
                raise NotFound("no such resource type")
            attr_map = {x.name: (x.id, ResourceViewSet.get_attribute_classname_by_attributeDefined(x.__class__.__name__))
                        for x in rd.attributes.all()}
            de_attr_map = {x.id: x.name for x in rd.attributes.all()}

            def tmpSerializer(*args, **kwargs):
                kwargs['attr_map'] = attr_map
                kwargs['de_attr_map'] = de_attr_map
                kwargs['resourceDefined'] = rd
                return serializers.ResourceSerializer(*args, **kwargs)

            setattr(self, 'my_sc', tmpSerializer)
            return tmpSerializer
        else:
            return sc

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        umap = { x.attributeDefined: x for x in instance.attributes.all()}
        for x in s.validated_data['attributes']:
            t = umap.get(x['attributeDefined'], None)
            if t is None:
                try:
                    resourcetype = x.pop('resourcetype')
                    x['resource'] = instance
                    adm = getattr(resource, resourcetype)
                    adm.objects.create(**x)
                except TypeError as err:
                    raise APIException("TypeError: %s is %s %s" % (x['attributeDefined'].name, x['attributeDefined'].__class__.__name__, str(err)))
            else:
                t.value = x['value']
                t.save()
        labels = s.validated_data.pop('labels')
        departments = s.validated_data.pop('departments')
        instance.departments.set(departments)
        instance.labels.all().delete()
        instance.labels.bulk_create([resource.Label(resource=instance, **label) for label in labels])
        instance.name = s.validated_data.get('name')
        instance.save()
        return Response({'success': True})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        for x in instance.attributes.all():
            x.delete()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LabelKeyViewSet(viewsets.ViewSet):
    def list(self, request):
        values = resource.Label.objects.values('k').distinct()
        return Response([x['k'] for x in values])


class LabelValueViewSet(viewsets.ViewSet):
    def list(self, request, label_k):
        values = resource.Label.objects.filter(k=label_k).values('v').distinct()
        return Response([x['v'] for x in values])