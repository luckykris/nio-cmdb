from django.db import models

from jsonfield import JSONField
from .base import BaseModel
from .hooks import HttpHook
from . import Department
# patch


class Proxy(BaseModel):
    name = models.CharField(u'proxy  name', max_length=255, blank=False, null=False, unique=True)
    plugin = models.CharField('plugin name', max_length=255, blank=False, null=False, default='')
    kwargs = JSONField('value', blank=True, null=True)

