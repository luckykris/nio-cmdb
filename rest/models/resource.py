from django.db import models
from django.contrib.contenttypes.models import ContentType
from polymorphic.models import PolymorphicModel, PolymorphicManager
from jsonfield import JSONField
from concurrency.fields import IntegerVersionField
from .base import BaseModel
from .hooks import HttpHook
from . import Department
from ..protect_keyword import PROTECT_NAME_LIST
from ..rest_exceptions import ProtectException
# patch
PolymorphicModel.polymorphic_ctype = models.ForeignKey(
        ContentType,
        null=True,
        editable=False,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name="polymorphic_%(app_label)s.%(class)s_set+",
    )


class ResourceDefined(BaseModel):
    _version = IntegerVersionField()
    name = models.CharField(u'resource defined name', max_length=255, blank=False, null=False, unique=True)
    enable_version_check = models.BooleanField(u'concurrency version update check', max_length=255, default=False)
    enable_rollback = models.BooleanField(u'rollback old version', max_length=255, default=False)
    create_hook = models.ForeignKey(HttpHook,
                                    default=None,
                                    null=True,
                                    related_name="create_hook",
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    db_constraint=False)
    update_hook = models.ForeignKey(HttpHook,
                                    default=None,
                                    null=True,
                                    related_name="update_hook",
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    db_constraint=False)
    delete_hook = models.ForeignKey(HttpHook,
                                    default=None,
                                    null=True,
                                    related_name="delete_hook",
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    db_constraint=False)


class AttributeDefined(PolymorphicModel, BaseModel):
    name = models.CharField('attribute define name', max_length=64, blank=False, null=False)
    resourceDefined = models.ForeignKey(
        ResourceDefined,
        db_constraint=False,
        on_delete=models.CASCADE,
        default=None,
        blank=False,
        related_name='attributes')
    objects = PolymorphicManager()

    def save(self, *args, **kwargs):
        if self.name in PROTECT_NAME_LIST:
            raise ProtectException("'%s' is a protect keyword" % self.name)
        super(AttributeDefined, self).save(*args, **kwargs)


class IntegerAttributeDefined(AttributeDefined):
    default = models.IntegerField('value', blank=True, null=True)


class PKIntegerAttributeDefined(AttributeDefined):
    default = models.IntegerField('value', blank=True, null=True)


class StringAttributeDefined(AttributeDefined):
    default = models.CharField('value', max_length=255, blank=True, null=True)


class PKStringAttributeDefined(AttributeDefined):
    default = models.CharField('value', max_length=255, blank=True, null=True)


class TextAttributeDefined(AttributeDefined):
    default = models.TextField('value', blank=True, null=True)


class FloatAttributeDefined(AttributeDefined):
    default = models.FloatField('value', blank=True, null=True)


class ObjectAttributeDefined(AttributeDefined):
    default = JSONField('value', blank=True, null=True)


class DatetimeAttributeDefined(AttributeDefined):
    default = models.DateTimeField('value', blank=True, null=True)


class DateAttributeDefined(AttributeDefined):
    default = models.DateField('value', blank=True, null=True)


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


class Attribute(PolymorphicModel):
    attributeDefined = models.ForeignKey(AttributeDefined, db_constraint=False, on_delete=models.CASCADE)
    resource = models.ForeignKey('Resource', db_constraint=False, on_delete=models.CASCADE, related_name='attributes', blank=True)
    objects = PolymorphicManager()


class IntegerAttribute(Attribute):
    value = models.IntegerField('value', blank=True, null=True, default=None)


class StringAttribute(Attribute):
    value = models.CharField('value', max_length=255, blank=True, null=True, default=None)


class PKIntegerAttribute(Attribute):
    atd = models.IntegerField("atd", null=False, default=None)
    value = models.IntegerField('value', blank=True,  default=None)

    class Meta:
        unique_together = (("atd", "value"),)


class PKStringAttribute(Attribute):
    atd = models.IntegerField("atd", null=False, default=None)
    value = models.CharField('value', max_length=255, blank=True)

    class Meta:
        unique_together = (("atd", "value"),)


class TextAttribute(Attribute):
    value = models.TextField('value', blank=True, null=True, default=None)


class FloatAttribute(Attribute):
    value = models.FloatField('value', blank=True, null=True, default=None)


class ObjectAttribute(Attribute):
    value = JSONField('value', blank=True, null=True, default=None)


class DatetimeAttribute(Attribute):
    value = models.DateTimeField('value', blank=True, null=True, default=None)


class DateAttribute(Attribute):
    value = models.DateField('value', blank=True, null=True, default=None)


class Many2ManyAttribute(Attribute):
    value = models.ManyToManyField(
        'Resource', blank=True)


class ForeignKeyAttribute(Attribute):
    value = models.ForeignKey(
        'Resource',
        db_constraint=False,
        null=True,
        on_delete=models.SET_NULL,
        default=None)


class Resource(BaseModel):
    id = models.UUIDField(auto_created=True, primary_key=True, default=BaseModel.gen_uuid, editable=False)
    name = models.CharField(u'resource defined name', max_length=255, blank=False, null=False)
    type = models.ForeignKey(ResourceDefined, db_constraint=False, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, blank=True)
    _version = IntegerVersionField()

    class Meta:
        ordering = ['_ctime']
        unique_together = ('type', 'name')


class Label(models.Model):
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='labels'
    )
    k = models.CharField(u'k', max_length=255, blank=False, null=False)
    v = models.CharField(u'v', max_length=255, blank=False, null=False)

    class Meta:
        unique_together = ["resource", "k", "v"]
        index_together = ["resource", "k", "v"]

    def __unicode__(self):
        return '%s: %s' % (self.k, self.v)


class BackupResource(BaseModel):
    version = models.BigIntegerField(auto_created=True)
    resource_id = models.ForeignKey(Resource, on_delete=models.DO_NOTHING, db_constraint=False)
    detail = JSONField()