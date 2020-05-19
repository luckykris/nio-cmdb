from mptt.models import MPTTModel, TreeForeignKey
from django.db import models
from . resource import Resource
import hashlib
from jsonfield import JSONField


class Service(MPTTModel):
    name = models.CharField(
        u'name',
        max_length=255,
        blank=False,
        null=False
    )
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_constraint=False)
    tree_path_cache = models.CharField(max_length=1024, blank=True, null=True, help_text="不可编辑字段,描述路径缓存")
    tree_path_md5 = models.CharField(max_length=64, blank=True, null=True, help_text="不可编辑字段,描述路径缓存", unique=True)
    env = JSONField('env', blank=True, null=True)
    resources = models.ManyToManyField(Resource, blank=True, db_constraint=False)

    def descendants(self):
        return self.get_descendants(include_self=True)

    def save(self, *args, **kwargs):
        self.tree_path_cache = self.path(new=False if self.pk else True)
        hash_md5 = hashlib.md5(self.tree_path_cache)
        self.tree_path_md5 = hash_md5.hexdigest()
        super(Service, self).save(*args, **kwargs)

    def path(self, new=False):
        p = [""]
        if new:
            s = self
            while s.parent:
                p.append(s.name)
                s = s.parent
            p.append(self.name)
            return '/'.join(p)

        for x in self.get_ancestors(ascending=False, include_self=False):
            p.append(x.name)
        p.append(self.name)
        return '/'.join(p)


class ServiceLabel(models.Model):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        db_constraint=False,
        related_name='labels'
    )
    k = models.CharField(u'k', max_length=255, blank=False, null=False)
    v = models.CharField(u'v', max_length=255, blank=False, null=False)

    class Meta:
        unique_together = ["service", "k", "v"]
        index_together = ["service", "k", "v"]

    def __unicode__(self):
        return '%s: %s' % (self.k, self.v)

