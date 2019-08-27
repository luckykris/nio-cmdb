from rest_framework import serializers, relations
from rest_polymorphic.serializers import PolymorphicSerializer
from rest_framework.fields import SkipField
from rest_framework.settings import api_settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from collections.abc import Mapping
from rest_framework.fields import get_error_detail, set_value
from rest_framework.utils import html, model_meta, representation
from rest_framework.relations import PKOnlyObject, empty
from rest_framework.exceptions import ErrorDetail, ValidationError
from django.db import transaction

from .models import User, Department


from rest_framework.utils import model_meta
import copy
from collections import OrderedDict
from .models import *


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'url', 'username', 'name', 'email', 'departments')


class DepartmentSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects, required=False)
    leaders = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects, required=False)

    class Meta:
        model = Department
        fields = "__all__"


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.Label
        fields = ('k', 'v')


class IntegerAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.IntegerAttributeDefined
        fields = "__all__"


class StringAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.StringAttributeDefined
        fields = "__all__"


class TextAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.TextAttributeDefined
        fields = "__all__"


class FloatAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.FloatAttributeDefined
        fields = "__all__"


class ObjectAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.ObjectAttributeDefined
        fields = "__all__"


class Many2ManyAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.Many2ManyAttributeDefined
        fields = "__all__"


class ForeignKeyAttributeDefinedSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.ForeignKeyAttributeDefined
        fields = "__all__"


class AttributeDefinedSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        resource.IntegerAttributeDefined: IntegerAttributeDefinedSerializer,
        resource.StringAttributeDefined: StringAttributeDefinedSerializer,
        resource.FloatAttributeDefined: FloatAttributeDefinedSerializer,
        resource.TextAttributeDefined: TextAttributeDefinedSerializer,
        resource.Many2ManyAttributeDefined: Many2ManyAttributeDefinedSerializer,
        resource.ObjectAttributeDefined: ObjectAttributeDefinedSerializer,
        resource.ForeignKeyAttributeDefined: ForeignKeyAttributeDefinedSerializer,
    }


class IntegerAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.IntegerAttribute
        fields = "__all__"


class StringAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.StringAttribute
        fields = "__all__"


class TextAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.TextAttribute
        fields = "__all__"


class FloatAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.FloatAttribute
        fields = "__all__"


class ObjectAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.ObjectAttribute
        fields = "__all__"


class Many2ManyAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.Many2ManyAttribute
        fields = "__all__"


class ForeignKeyAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = resource.ForeignKeyAttribute
        fields = "__all__"


class AttributeSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        resource.IntegerAttribute: IntegerAttributeSerializer,
        resource.StringAttribute: StringAttributeSerializer,
        resource.FloatAttribute: FloatAttributeSerializer,
        resource.TextAttribute: TextAttributeSerializer,
        resource.ObjectAttribute: ObjectAttributeSerializer,
        resource.Many2ManyAttribute: Many2ManyAttributeSerializer,
        resource.ForeignKeyAttribute: ForeignKeyAttributeSerializer,
    }


class ResourceDefinedSerializer(serializers.ModelSerializer):
    attributes = AttributeDefinedSerializer(many=True, required=True)

    def create(self, validated_data):
        attributes = validated_data.pop('attributes', [])
        with transaction.atomic():
            r = self.Meta.model.objects.create(**validated_data)
            for attribute in attributes:
                resourcetype = attribute.pop('resourcetype')
                attribute['resourceDefined'] = r
                getattr(resource, resourcetype).objects.create(**attribute)
        return r

    class Meta:
        model = resource.ResourceDefined
        fields = "__all__"


class ResourceSerializer(serializers.ModelSerializer):
    attributes = AttributeSerializer(many=True, required=False)
    labels = LabelSerializer(many=True, required=False)

    def __init__(self, *args, **kwargs):
        self.attr_map = kwargs.pop('attr_map', {})
        self.de_attr_map = kwargs.pop('de_attr_map', {})
        self.resourceDefined = kwargs.pop('resourceDefined', None)
        super(ResourceSerializer,self).__init__(*args, **kwargs)
    # def __init__(self, instance=None, data=empty, **kwargs):
    #     self.instance = instance
    #     if data is not empty:
    #         self.initial_data = data
    #     self.partial = kwargs.pop('partial', False)
    #     self._context = kwargs.pop('context', {})
    #     kwargs.pop('many', None)
    #     self.attr_map = kwargs.pop('attr_map', {})
    #     self.de_attr_map = kwargs.pop('de_attr_map', {})
    #     self.resourceDefined = kwargs.pop('resourceDefined', None)
    #     super().__init__(**kwargs)

    def to_internal_value(self, data):
        """
                Dict of native values <- Dict of primitive datatypes.
                """
        if not isinstance(data, Mapping):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        data['attributes'] = []
        ret = OrderedDict()
        ret['type'] = self.resourceDefined
        errors = OrderedDict()
        fields = self._writable_fields
        for k, v in self.attr_map.items():
            data['attributes'].append({'value': data.get(k, None), 'attributeDefined': v[0], 'resourcetype': v[1]})
        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                set_value(ret, field.source_attrs, validated_value)
        if errors:
            raise ValidationError(errors)
        return ret

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields
        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)
        attributes = ret.pop('attributes')
        for k, v in self.de_attr_map.items():
            # 等attributeDefined增加时可以同时增加资源的attribute属性的时候 可以增加默认值功能,否则影响filter功能
            # ret[v.name] = v.default
            ret[v.name] = None
        for attr in attributes:
            ret[self.de_attr_map[attr['attributeDefined']].name] = attr['value']
        return ret

    def create(self, validated_data):
        with transaction.atomic():
            attributes = validated_data.pop('attributes', [])
            labels = validated_data.pop('labels', [])
            departments = validated_data.pop('departments', [])
            r = self.Meta.model.objects.create(**validated_data)
            r.departments.set(departments)
            for x in attributes:
                x['resource'] = r
                resourcetype = x.pop('resourcetype')
                a = getattr(resource, resourcetype)
                if a == resource.Many2ManyAttribute:
                    value = x.pop('value')
                    for y in value:
                        assert y.type == x['attributeDefined'].relate
                    m2m = a.objects.create(**x)
                    m2m.value.set(value)
                elif a == resource.ForeignKeyAttribute:
                    assert x['value'].type == x['attributeDefined'].relate
                    a.objects.create(**x)
            r.labels.bulk_create([resource.Label(resource=r, **label) for label in labels])
        return r

    class Meta:
        model = resource.Resource
        fields = ('id', 'name', 'attributes', 'labels',  '_ctime', '_mtime', 'departments')