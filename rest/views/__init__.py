import uuid
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, NotFound
from rest_framework.filters import OrderingFilter, SearchFilter, BaseFilterBackend
from django_filters.rest_framework import filters, filterset, DjangoFilterBackend
from django.db import transaction
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import status, mixins
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from mptt.templatetags.mptt_tags import cache_tree_children, get_cached_trees
from ..models import *
from ..models import Department, User
from .. import serializers
import logging
from ..version import VERSION_STRING
logger = logging.getLogger('audit')

index_view = never_cache(TemplateView.as_view(template_name='index.html'))


class EnvViewSet(APIView):

    def get(self, request):
        return Response({'version': VERSION_STRING})


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk
        })


class MineViewSet(APIView):

    def get(self, request):
        user = self.request.user
        serializer_context = {
            'request': request,
        }
        serializer = serializers.UserSerializer(user, context=serializer_context)
        return Response(serializer.data)


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


class HookViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = serializers.HookSerializer
    queryset = hooks.BaseHook.objects.all()


class HookServerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = serializers.HookServerSerializer
    queryset = hooks.HookServer.objects.all()


# Create your views here.
class DepartmentViewSet(viewsets.ModelViewSet):
    # authentication_classes = (authentication.JWTAuthentication,)
    # permission_classes = (permissions.IsAuthenticated,)
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Department.objects.all()
    serializer_class = serializers.DepartmentSerializer


class AttributeDefinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = resource.AttributeDefined.objects.all()
    serializer_class = serializers.AttributeDefinedSerializer


class ResourceDefinedIdsFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        ids = request.query_params.getlist('[]ids', None)
        if ids:
            queryset = queryset.filter(pk__in=ids)
        return queryset


class ResourceDefinedViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = resource.ResourceDefined.objects.all()
    serializer_class = serializers.ResourceDefinedSerializer
    filter_backends = [ResourceDefinedIdsFilterBackend,  SearchFilter, OrderingFilter]
    search_fields = ('$name',)
    ordering_fields = ('name', '_ctime', '_mtime')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        with transaction.atomic():
            for x in instance.attributes.all():
                x.delete()
            self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        # 重写源码get_object操作
        # filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        value = self.kwargs[lookup_url_kwarg]
        try:
            int(value)
            filter_kwargs = {self.lookup_field: value}
        except (AttributeError, ValueError):
            filter_kwargs = {'name': value}

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class AttributeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = resource.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer


class ResourceViewSet(viewsets.ModelViewSet):

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ('$id', '$name', '$departments__name', '$labels__k', '$labels__v')
    filterset_fields = ('name',)
    ordering_fields = ('name', '_ctime', '_mtime')

    @staticmethod
    def get_attribute_classname_by_attribute_defined(x):
        return x[:-7]

    # def get_m2m_or_fk_attr(self ):

    def get_resource_defined(self):
        resource_defined = self.kwargs.get('resource_defined')
        resource_id = self.kwargs.get('resource_id')
        m2m_or_fk_attr = self.kwargs.get('m2m_or_fk_attr')
        rd = getattr(self, 'rd', None)
        if rd is None:
            rd = resource.ResourceDefined.objects.prefetch_related('attributes').get(name=resource_defined)
            if resource_id and m2m_or_fk_attr:
                attr_defined = rd.attributes.get(name=m2m_or_fk_attr)
                if isinstance(attr_defined, resource.Many2ManyAttributeDefined):
                    second_rd = resource.ResourceDefined.objects.prefetch_related('attributes').get(pk=attr_defined.relate.pk)
                    setattr(self, 'nest_resource_id', resource_id)
                    setattr(self, 'm2m_attr_defined', attr_defined)
                    rd = second_rd
                elif isinstance(attr_defined, resource.ForeignKeyAttributeDefined):
                    second_rd = resource.ResourceDefined.objects.prefetch_related('attributes').get(
                        pk=attr_defined.relate.pk)
                    setattr(self, 'nest_resource_id', resource_id)
                    setattr(self, 'fk_attr_defined', attr_defined)
                    rd = second_rd
            setattr(self, 'rd', rd)
        return rd

    def filter_queryset_from_request(self, queryset):
        rd = self.get_resource_defined()
        m = {x.name: x for x in rd.attributes.all()}
        fqs = []
        # name = None
        for k, v in self.request.query_params.items():
            # 过滤空参数
            if v == '':
                continue
            if k.startswith('~'):
                k2 = k[1:]
                pattern = "%s___value__iregex"
            elif k.startswith('gte__'):
                k2 = k[5:]
                pattern = "%s___value__gte"
            elif k.startswith('gt__'):
                k2 = k[4:]
                pattern = "%s___value__gt"
            elif k.startswith('lte__'):
                k2 = k[5:]
                pattern = "%s___value__lte"
            elif k.startswith('lt__'):
                k2 = k[4:]
                pattern = "%s___value__lt"
            else:
                k2 = k
                pattern = "%s___value"
            if k2 in m:
                acn = self.get_attribute_classname_by_attribute_defined(m[k2].__class__.__name__)
                q_kwargs = {pattern % acn: v}
                tmp_fq = Q(attributeDefined=m[k2]) & Q(**q_kwargs)
                fqs.append(tmp_fq)
        for fq in fqs:
            queryset = queryset.filter(attributes__in=resource.Attribute.objects.filter(fq).all())
        return queryset

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        # 重写源码get_object操作
        # filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        value = self.kwargs[lookup_url_kwarg]
        try:
            uuid.UUID(value)
            filter_kwargs = {self.lookup_field: value}
        except (AttributeError, ValueError):
            filter_kwargs = {'name': value}

        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self):
        try:
            rd = self.get_resource_defined()
            m2m_attr_defined = getattr(self, 'm2m_attr_defined', None)
            fk_attr_defined = getattr(self, 'fk_attr_defined', None)
            resource_id = getattr(self, 'nest_resource_id', None)
            if resource_id is not None and m2m_attr_defined is not None:
                queryset_condition = resource.Resource.objects.get(pk=resource_id)\
                    .attributes.filter(attributeDefined=m2m_attr_defined)
                queryset = resource.Resource.objects.filter(many2manyattribute__in=queryset_condition).filter(type=rd) \
                    .prefetch_related('departments', 'labels', 'attributes').distinct()
            elif resource_id is not None and fk_attr_defined is not None:
                queryset_condition = resource.Resource.objects.get(name=resource_id)\
                    .attributes.filter(attributeDefined=fk_attr_defined)
                queryset = resource.Resource.objects.filter(foreignkeyattribute__in=queryset_condition).filter(type=rd) \
                    .prefetch_related('departments', 'labels', 'attributes').distinct()
            else:
                queryset = resource.Resource.objects.filter(type=rd)\
                    .prefetch_related('departments', 'labels', 'attributes').distinct()
            queryset = self.filter_queryset_from_request(queryset)
        except Exception as e:
            raise NotFound('not found resource: %r' % e)
        return queryset

    def get_serializer_class(self):
        # compatibilized the rest-framework docs api
        if self.request is None:
            return serializers.ResourceSerializer
        sc = getattr(self, 'my_sc', None)
        if sc is None:
            select_fields = self.get_fields_filter_from_request()
            setattr(self, 'select_fields', select_fields)
            rd = self.get_resource_defined()
            attr_map = {
                x.name: (
                    x.id,
                    ResourceViewSet.get_attribute_classname_by_attribute_defined(x.__class__.__name__),
                    x
                ) for x in rd.attributes.all()
            }
            de_attr_map = {x.id: x for x in rd.attributes.all()}

            def tmp_serializer(*args, **kwargs):
                kwargs['attr_map'] = attr_map
                kwargs['de_attr_map'] = de_attr_map
                kwargs['resourceDefined'] = rd
                kwargs['select_fields'] = select_fields
                return serializers.ResourceSerializer(*args, **kwargs)

            setattr(self, 'my_sc', tmp_serializer)
            return tmp_serializer
        else:
            return sc

    def get_fields_filter_from_request(self):
        select_fields = self.request.query_params.get('fields', None)
        if select_fields:
            select_fields = select_fields.split(',')
        else:
            select_fields = None
        return select_fields

    def destroy(self, request, *args, **kwargs):
        with transaction.atomic():
            instance = self.get_object()
            for x in instance.attributes.all():
                x.delete()
            instance.delete()
            # delete hook
            if instance.type.create_hook is not None:
                instance.type.create_hook.trigger(self.get_serializer_class().to_representation(instance))
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def distinct(self, request, resource_defined):
        column = request.query_params.get('column')
        rd = self.get_resource_defined()
        try:
            atd = rd.attributes.get(name=column)
        except resource.AttributeDefined.DoesNotExist:
            return Response(status=404, data={'code': '404', 'detail': 'no such column'})
        r = set(
            [x.value
             for x in resource.Attribute.objects.filter(attributeDefined=atd)
             if hasattr(x, 'value')]
        )
        return Response(r)

    @action(detail=False, methods=['get'])
    def groupby(self, request, resource_defined):
        column = request.query_params.get('column')
        rd = self.get_resource_defined()
        try:
            atd = rd.attributes.get(name=column)
        except resource.AttributeDefined.DoesNotExist:
            return Response(status=404, data={'code': '404', 'detail': 'no such column'})
        r = [x.value
             for x in resource.Attribute.objects.filter(attributeDefined=atd)
             if hasattr(x, 'value')]
        r_m = {}
        for x in r:
            if x in r_m:
                r_m[x] += 1
            else:
                r_m[x] = 1
        return Response(r_m)

    @action(detail=False, methods=['get'])
    def count(self, request, resource_defined):
        rd = self.get_resource_defined()
        c = resource.Resource.objects.filter(type=rd).all().count()
        return Response({'count': c, 'resource-defined': rd.name})


class LabelKeyViewSet(viewsets.ViewSet):
    def list(self, request):
        values = resource.Label.objects.values('k').distinct()
        return Response([x['k'] for x in values])


class LabelValueViewSet(viewsets.ViewSet):
    def list(self, request, label_k):
        values = resource.Label.objects.filter(k=label_k).values('v').distinct()
        return Response([x['v'] for x in values])


class TreeFilterBackend(BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        queryset = service.Service.objects.get_queryset_descendants(queryset, include_self=True).prefetch_related('labels')
        queryset = service.Service.objects.get_queryset_ancestors(queryset, include_self=True).prefetch_related('labels')
        queryset = cache_tree_children(queryset)
        return queryset


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ServiceSerializer
    queryset = service.Service.objects.prefetch_related('labels')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['level', 'name']
    search_fields = ('$id', '$name', '$labels__k', '$labels__v')
    ordering_fields = ('name', '_ctime', '_mtime')


class ServiceTreeViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ServiceTreeSerializer
    queryset = service.Service.objects.select_related('parent').prefetch_related('labels')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter, TreeFilterBackend]
    filterset_fields = ['level', 'name', 'id']
    search_fields = ('$id', '$name', '$labels__k', '$labels__v')
    ordering_fields = ('name', '_ctime', '_mtime')


class ProxyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    serializer_class = serializers.ProxySerializer
    queryset = proxy.Proxy.objects.all()


class BackupResourceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.BackupResourceSerializer
    queryset = resource.BackupResource.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['resource_id', 'version']
    ordering_fields = ('_ctime', '_mtime')