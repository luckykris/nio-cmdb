from django.db import models
from polymorphic.models import PolymorphicModel, PolymorphicManager
from jsonfield import JSONField
from .base import BaseModel
from . import Department


class ResourceDefined(BaseModel):
    name = models.CharField(u'resource defined name', max_length=64, blank=False, null=False)


class AttributeDefined(PolymorphicModel, BaseModel):
    name = models.CharField('attribute define name', max_length=64, blank=False, null=False)
    resourceDefined = models.ForeignKey(
        ResourceDefined,
        db_constraint=False,
        on_delete=models.CASCADE,
        default=None,
        related_name='attributes')
    objects = PolymorphicManager()


class IntegerAttributeDefined(AttributeDefined):
    default = models.IntegerField('value', blank=True, null=True)


class StringAttributeDefined(AttributeDefined):
    default = models.CharField('value', max_length=64, blank=True, null=True)


class TextAttributeDefined(AttributeDefined):
    default = models.TextField('value', blank=True, null=True)


class FloatAttributeDefined(AttributeDefined):
    default = models.FloatField('value', blank=True, null=True)


class ObjectAttributeDefined(AttributeDefined):
    default = JSONField('value', blank=True, null=True)


class Many2ManyAttributeDefined(AttributeDefined):
    relate = models.ForeignKey(
        ResourceDefined,
        db_constraint=False,
        on_delete=models.CASCADE,
        null=False,)


class ForeignKeyAttributeDefined(AttributeDefined):
    relate = models.ForeignKey(
        ResourceDefined,
        db_constraint=False,
        on_delete=models.CASCADE,
        null=False,)


class Resource(BaseModel):
    id = models.UUIDField(auto_created=True, primary_key=True, default=BaseModel.gen_uuid, editable=False)
    name = models.CharField(u'resource defined name', max_length=64, blank=False, null=False)
    type = models.ForeignKey(ResourceDefined, db_constraint=False, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, blank=True)


class Label(models.Model):
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, db_constraint=False, related_name='labels')
    k = models.CharField(u'k', max_length=64, blank=False, null=False)
    v = models.CharField(u'v', max_length=64, blank=False, null=False)

    class Meta:
        unique_together = ["resource", "k", "v"]
        index_together = ["resource", "k", "v"]

    def __unicode__(self):
        return '%s: %s' % (self.k, self.v)


class Attribute(PolymorphicModel):
    attributeDefined = models.ForeignKey(AttributeDefined, db_constraint=False, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, db_constraint=False, on_delete=models.CASCADE, related_name='attributes', blank=True)
    objects = PolymorphicManager()


class IntegerAttribute(Attribute):
    value = models.IntegerField('value', blank=True, null=True, default=None)


class StringAttribute(Attribute):
    value = models.CharField('value', max_length=64, blank=True, null=True, default=None)


class TextAttribute(Attribute):
    value = models.TextField('value', blank=True, null=True, default=None)


class FloatAttribute(Attribute):
    value = models.FloatField('value', blank=True, null=True, default=None)


class ObjectAttribute(Attribute):
    value = JSONField('value', blank=True, null=True, default=None)


class Many2ManyAttribute(Attribute):
    value = models.ManyToManyField(
        Resource)


class ForeignKeyAttribute(Attribute):
    value = models.ForeignKey(
        Resource,
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        default=None)

